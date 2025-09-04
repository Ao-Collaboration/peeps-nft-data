#!/usr/bin/env python3
"""
Peeps NFT Cull Script

This script queries the Ethereum contract to get the official list of token IDs
and removes any local files that aren't part of the official collection.

Usage:
    python cull_script.py --peep-dir ../peep
    python cull_script.py --peep-dir ../peep --dry-run
    python cull_script.py --peep-dir ../peep --rpc-url https://mainnet.infura.io/v3/YOUR_KEY
"""

import argparse
import os
import sys
import json
import logging
import re
from pathlib import Path
from typing import Set, List, Optional
import requests
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Contract details
CONTRACT_ADDRESS = "0x383a7b0488756b5618f4ce2bcbc608ad48f09a57"
MAINNET_RPC_URL = "https://eth.llamarpc.com"  # Free public endpoint

# ERC-721 ABI for the functions we need
ERC721_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]


class PeepsCuller:
    def __init__(self, peep_dir: str, rpc_url: str = MAINNET_RPC_URL, dry_run: bool = False):
        """
        Initialize the Peeps culler.
        
        Args:
            peep_dir: Directory containing the peep files
            rpc_url: Ethereum RPC URL
            dry_run: If True, only show what would be deleted without actually deleting
        """
        self.peep_dir = Path(peep_dir)
        self.dry_run = dry_run
        self.rpc_url = rpc_url
        
        # Validate peep directory
        if not self.peep_dir.exists():
            raise ValueError(f"Peep directory does not exist: {peep_dir}")
        
        # Initialize Web3 with timeout
        from web3.middleware import ExtraDataToPOAMiddleware
        self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum RPC: {rpc_url}")
        
        # Add PoA middleware for some networks
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # Create contract instance
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=ERC721_ABI
        )
        
        logger.info(f"Connected to Ethereum mainnet via {rpc_url}")
        logger.info(f"Contract address: {CONTRACT_ADDRESS}")
        logger.info(f"Web3 connection status: {self.w3.is_connected()}")
        logger.info(f"Latest block number: {self.w3.eth.block_number}")
    
    def get_total_supply(self) -> int:
        """Get the total supply from the contract."""
        try:
            total_supply = self.contract.functions.totalSupply().call()
            logger.info(f"Total supply: {total_supply}")
            return total_supply
        except Exception as e:
            logger.error(f"Error getting total supply: {e}")
            raise
    
    def get_token_uri(self, token_id: int, max_retries: int = 3) -> Optional[str]:
        """Get the token URI for a given token ID with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.debug(f"Calling tokenURI({token_id}) on contract... (attempt {attempt + 1}/{max_retries})")
                uri = self.contract.functions.tokenURI(token_id).call()
                logger.debug(f"Successfully got URI for token {token_id}: {uri}")
                return uri
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error getting token URI for token {token_id} (attempt {attempt + 1}): {e}. Retrying...")
                    import time
                    time.sleep(1)  # Wait 1 second before retry
                else:
                    logger.warning(f"Error getting token URI for token {token_id} after {max_retries} attempts: {e}")
                    return None
        return None
    
    def extract_token_id_from_uri(self, uri: str) -> Optional[str]:
        """
        Extract token ID from URI.
        Example: https://api.peeps.club/peep/18089409297514631661.json -> 18089409297514631661
        """
        # Look for the pattern: /peep/{token_id}.json
        match = re.search(r'/peep/(\d+)\.json', uri)
        if match:
            return match.group(1)
        return None
    
    def get_official_token_ids(self) -> Set[str]:
        """Get all official token IDs from the contract."""
        logger.info("Fetching official token IDs from contract...")
        
        total_supply = self.get_total_supply()
        official_ids = set()
        
        logger.info(f"Processing {total_supply} tokens...")
        
        for token_id in range(total_supply):
            if token_id % 5 == 0:  # Log progress every 5 tokens for more frequent updates
                logger.info(f"Processing token {token_id}/{total_supply} ({token_id/total_supply*100:.1f}%) - Found {len(official_ids)} so far")
            
            logger.debug(f"Getting URI for token ID {token_id}")
            uri = self.get_token_uri(token_id)
            if uri:
                logger.debug(f"Got URI for token {token_id}: {uri}")
                extracted_id = self.extract_token_id_from_uri(uri)
                if extracted_id:
                    official_ids.add(extracted_id)
                    logger.debug(f"Found official token ID: {extracted_id}")
                else:
                    logger.warning(f"Could not extract token ID from URI: {uri}")
            else:
                logger.warning(f"No URI found for token ID {token_id}")
            
            # Add a small delay to avoid overwhelming the RPC endpoint
            if token_id % 10 == 0 and token_id > 0:
                import time
                time.sleep(0.1)  # 100ms delay every 10 requests
        
        logger.info(f"Found {len(official_ids)} official token IDs")
        return official_ids
    
    def get_local_files(self) -> Set[str]:
        """Get all local JSON files (without extension)."""
        local_files = set()
        
        for file_path in self.peep_dir.glob("*.json"):
            # Remove .json extension to get the base name
            base_name = file_path.stem
            local_files.add(base_name)
        
        logger.info(f"Found {len(local_files)} local JSON files")
        return local_files
    
    def get_files_to_delete(self, official_ids: Set[str], local_files: Set[str]) -> Set[str]:
        """Get the set of files that should be deleted."""
        files_to_delete = local_files - official_ids
        logger.info(f"Files to delete: {len(files_to_delete)}")
        return files_to_delete
    
    def delete_files(self, files_to_delete: Set[str]) -> dict:
        """Delete the specified files and their associated images."""
        deleted_files = {
            'json': 0,
            'png': 0,
            'svg': 0,
            'total': 0
        }
        
        for base_name in files_to_delete:
            # Delete JSON file
            json_file = self.peep_dir / f"{base_name}.json"
            if json_file.exists():
                if not self.dry_run:
                    json_file.unlink()
                logger.info(f"{'[DRY RUN] Would delete' if self.dry_run else 'Deleted'}: {json_file.name}")
                deleted_files['json'] += 1
            
            # Delete PNG file
            png_file = self.peep_dir / f"{base_name}.png"
            if png_file.exists():
                if not self.dry_run:
                    png_file.unlink()
                logger.info(f"{'[DRY RUN] Would delete' if self.dry_run else 'Deleted'}: {png_file.name}")
                deleted_files['png'] += 1
            
            # Delete SVG file
            svg_file = self.peep_dir / f"{base_name}.svg"
            if svg_file.exists():
                if not self.dry_run:
                    svg_file.unlink()
                logger.info(f"{'[DRY RUN] Would delete' if self.dry_run else 'Deleted'}: {svg_file.name}")
                deleted_files['svg'] += 1
            
            deleted_files['total'] += 1
        
        return deleted_files
    
    def cull_files(self) -> dict:
        """Main method to cull files."""
        import time
        start_time = time.time()
        logger.info("Starting cull process...")
        
        # Get official token IDs
        logger.info("Step 1: Getting official token IDs from contract...")
        official_start = time.time()
        official_ids = self.get_official_token_ids()
        official_time = time.time() - official_start
        logger.info(f"Step 1 completed in {official_time:.2f} seconds")
        
        # Get local files
        logger.info("Step 2: Scanning local files...")
        local_start = time.time()
        local_files = self.get_local_files()
        local_time = time.time() - local_start
        logger.info(f"Step 2 completed in {local_time:.2f} seconds")
        
        # Find files to delete
        logger.info("Step 3: Comparing files to find what needs to be deleted...")
        compare_start = time.time()
        files_to_delete = self.get_files_to_delete(official_ids, local_files)
        compare_time = time.time() - compare_start
        logger.info(f"Step 3 completed in {compare_time:.2f} seconds")
        
        if not files_to_delete:
            logger.info("No files need to be deleted. All local files are official.")
            return {'deleted': {'json': 0, 'png': 0, 'svg': 0, 'total': 0}}
        
        # Show what will be deleted
        logger.info(f"Files to be deleted: {sorted(files_to_delete)}")
        
        # Delete files
        logger.info("Step 4: Deleting files...")
        delete_start = time.time()
        deleted_files = self.delete_files(files_to_delete)
        delete_time = time.time() - delete_start
        logger.info(f"Step 4 completed in {delete_time:.2f} seconds")
        
        total_time = time.time() - start_time
        logger.info(f"\nCull completed in {total_time:.2f} seconds!")
        logger.info(f"Deleted JSON files: {deleted_files['json']}")
        logger.info(f"Deleted PNG files: {deleted_files['png']}")
        logger.info(f"Deleted SVG files: {deleted_files['svg']}")
        logger.info(f"Total file groups deleted: {deleted_files['total']}")
        
        return {'deleted': deleted_files}


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Cull non-official Peeps NFT files based on Ethereum contract",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --peep-dir ../peep
  %(prog)s --peep-dir ../peep --dry-run
  %(prog)s --peep-dir ../peep --rpc-url https://mainnet.infura.io/v3/YOUR_KEY

This script will:
1. Query the Ethereum contract to get totalSupply()
2. Call tokenURI(uint256) for each token (0 to totalSupply-1)
3. Extract token IDs from the URIs
4. Delete any local files that aren't in the official list

Environment Variables (can be set in .env file or system environment):
  ETHEREUM_RPC_URL: Ethereum RPC URL (default: https://eth-mainnet.g.alchemy.com/v2/demo)
  PEEP_DIR: Directory containing the peep files (can be overridden with --peep-dir)
        """
    )
    
    parser.add_argument(
        '--peep-dir',
        default=os.getenv('PEEP_DIR'),
        help='Directory containing the peep files (e.g., ../peep) (default: PEEP_DIR env var)'
    )
    
    parser.add_argument(
        '--rpc-url',
        default=os.getenv('ETHEREUM_RPC_URL', MAINNET_RPC_URL),
        help=f'Ethereum RPC URL (default: ETHEREUM_RPC_URL env var or {MAINNET_RPC_URL})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.peep_dir:
        logger.error("Peep directory is required. Set PEEP_DIR environment variable or use --peep-dir argument")
        sys.exit(1)
    
    try:
        # Create culler and run
        culler = PeepsCuller(
            peep_dir=args.peep_dir,
            rpc_url=args.rpc_url,
            dry_run=args.dry_run
        )
        
        results = culler.cull_files()
        
        # Exit with appropriate code
        if results['deleted']['total'] > 0:
            logger.info(f"Successfully processed {results['deleted']['total']} file groups")
        else:
            logger.info("No files needed to be deleted")
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("\nCull interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during cull: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
