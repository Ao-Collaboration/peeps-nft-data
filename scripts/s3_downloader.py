#!/usr/bin/env python3
"""
S3 Bucket Content Downloader

This script downloads all content from a specified S3 bucket to a local directory.
It supports various configuration options and provides progress tracking.

Usage:
    python s3_downloader.py --bucket my-bucket-name --output ./downloads
    python s3_downloader.py --bucket my-bucket-name --output ./downloads --prefix images/
    python s3_downloader.py --bucket my-bucket-name --output ./downloads --dry-run

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    AWS_DEFAULT_REGION: AWS region (default: us-east-1)
"""

import argparse
import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path
import logging
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class S3Downloader:
    def __init__(self, bucket_name: str, output_dir: str, region: str = 'us-east-1', 
                 prefix: str = '', max_workers: int = 10, dry_run: bool = False):
        """
        Initialize the S3 downloader.
        
        Args:
            bucket_name: Name of the S3 bucket
            output_dir: Local directory to save downloaded files
            region: AWS region
            prefix: S3 prefix to filter objects (optional)
            max_workers: Maximum number of concurrent download threads
            dry_run: If True, only list objects without downloading
        """
        self.bucket_name = bucket_name
        self.output_dir = Path(output_dir)
        self.region = region
        self.prefix = prefix
        self.max_workers = max_workers
        self.dry_run = dry_run
        
        # Create output directory if it doesn't exist
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=region)
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure your credentials.")
            sys.exit(1)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Bucket '{bucket_name}' not found or access denied.")
            else:
                logger.error(f"Error accessing bucket: {e}")
            sys.exit(1)
    
    def list_objects(self) -> List[dict]:
        """List all objects in the bucket with the specified prefix."""
        objects = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        
        try:
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=self.prefix
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    objects.extend(page['Contents'])
            
            logger.info(f"Found {len(objects)} objects to download")
            return objects
            
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []
    
    def download_object(self, obj: dict) -> bool:
        """Download a single object from S3."""
        key = obj['Key']
        size = obj['Size']
        
        # Skip directories (S3 objects ending with '/')
        if key.endswith('/'):
            logger.debug(f"Skipping directory: {key}")
            return True
        
        # Create local file path
        local_path = self.output_dir / key
        
        # Create parent directories
        if not self.dry_run:
            local_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would download: {key} ({size} bytes)")
            return True
        
        try:
            # Download the object
            self.s3_client.download_file(
                self.bucket_name,
                key,
                str(local_path)
            )
            
            logger.info(f"Downloaded: {key} ({size} bytes)")
            return True
            
        except ClientError as e:
            logger.error(f"Error downloading {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {key}: {e}")
            return False
    
    def download_all(self) -> dict:
        """Download all objects from the bucket."""
        start_time = time.time()
        
        # List all objects
        objects = self.list_objects()
        if not objects:
            logger.warning("No objects found to download")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        if self.dry_run:
            logger.info("Dry run completed. No files were downloaded.")
            return {'success': len(objects), 'failed': 0, 'total': len(objects)}
        
        # Download objects concurrently
        success_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_obj = {
                executor.submit(self.download_object, obj): obj 
                for obj in objects
            }
            
            # Process completed downloads
            for future in as_completed(future_to_obj):
                obj = future_to_obj[future]
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Exception downloading {obj['Key']}: {e}")
                    failed_count += 1
        
        # Calculate statistics
        total_time = time.time() - start_time
        total_size = sum(obj['Size'] for obj in objects)
        
        logger.info(f"\nDownload completed!")
        logger.info(f"Successfully downloaded: {success_count} files")
        logger.info(f"Failed downloads: {failed_count} files")
        logger.info(f"Total size: {total_size / (1024*1024):.2f} MB")
        logger.info(f"Time taken: {total_time:.2f} seconds")
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(objects),
            'total_size': total_size,
            'time_taken': total_time
        }


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Download all content from an S3 bucket",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --bucket my-bucket --output ./downloads
  %(prog)s --bucket my-bucket --output ./downloads --prefix images/
  %(prog)s --bucket my-bucket --output ./downloads --dry-run
  %(prog)s --bucket my-bucket --output ./downloads --max-workers 20

Environment Variables (can be set in .env file or system environment):
  AWS_ACCESS_KEY_ID: AWS access key
  AWS_SECRET_ACCESS_KEY: AWS secret key
  AWS_DEFAULT_REGION: AWS region (default: us-east-1)
  S3_BUCKET_NAME: S3 bucket name (can be overridden with --bucket)
        """
    )
    
    parser.add_argument(
        '--bucket',
        default=os.getenv('S3_BUCKET_NAME'),
        help='Name of the S3 bucket to download from (default: S3_BUCKET_NAME env var)'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='Local directory to save downloaded files'
    )
    
    parser.add_argument(
        '--region',
        default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        help='AWS region (default: us-east-1)'
    )
    
    parser.add_argument(
        '--prefix',
        default='',
        help='S3 prefix to filter objects (optional)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=10,
        help='Maximum number of concurrent download threads (default: 10)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List objects without downloading them'
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
    if not args.bucket:
        logger.error("Bucket name is required. Set S3_BUCKET_NAME environment variable or use --bucket argument")
        sys.exit(1)
    
    if args.max_workers < 1:
        logger.error("max-workers must be at least 1")
        sys.exit(1)
    
    # Create downloader and run
    try:
        downloader = S3Downloader(
            bucket_name=args.bucket,
            output_dir=args.output,
            region=args.region,
            prefix=args.prefix,
            max_workers=args.max_workers,
            dry_run=args.dry_run
        )
        
        results = downloader.download_all()
        
        # Exit with appropriate code
        if results['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
