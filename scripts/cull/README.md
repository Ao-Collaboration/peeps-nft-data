# Peeps NFT Cull Script

A Python script that queries the Ethereum contract to get the official list of Peeps NFT token IDs and removes any local files that aren't part of the official collection.

## Features

- **Ethereum Contract Integration**: Queries the official Peeps contract to get the complete list of valid token IDs
- **Smart File Detection**: Automatically finds and removes non-official files while preserving associated images
- **Dry Run Mode**: Preview what would be deleted without actually deleting files
- **Comprehensive Logging**: Detailed logging of all operations and results
- **Error Handling**: Robust error handling for network and contract issues

## Installation

1. Set up a virtual environment:

```bash
cd scripts/cull
./setup_venv.sh
```

2. Activate the virtual environment:

```bash
source venv/bin/activate
```

### Configure Environment Variables

After installation, configure your environment variables (choose one method):

**Option A: .env file (Recommended)**

```bash
cp .env.example .env
# Edit .env with your actual values
```

**Option B: Environment Variables**

```bash
export ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
export PEEP_DIR=../../peep
```

## Usage

### Basic Usage

Cull non-official files from the peep directory:

```bash
# If using .env file or environment variables:
python cull_script.py

# Or specify directory explicitly:
python cull_script.py --peep-dir ../../peep
```

### Dry Run (Recommended First)

See what would be deleted without actually deleting:

```bash
python cull_script.py --dry-run
```

### Advanced Usage

Use a custom RPC endpoint:

```bash
python cull_script.py --rpc-url https://mainnet.infura.io/v3/YOUR_KEY
```

Enable verbose logging:

```bash
python cull_script.py --verbose
```

### Command Line Options

| Option          | Description                              | Default                |
| --------------- | ---------------------------------------- | ---------------------- |
| `--peep-dir`    | Directory containing the peep files     | PEEP_DIR env var       |
| `--rpc-url`     | Ethereum RPC URL                         | ETHEREUM_RPC_URL env var |
| `--dry-run`     | Show what would be deleted without deleting | False                  |
| `--verbose`     | Enable verbose logging                   | False                  |

### Environment Variables

| Variable                | Description    | Default   |
| ----------------------- | -------------- | --------- |
| `ETHEREUM_RPC_URL`      | Ethereum RPC URL | https://eth-mainnet.g.alchemy.com/v2/demo |
| `PEEP_DIR`              | Directory containing the peep files | - |

## How It Works

1. **Contract Query**: Connects to the Ethereum mainnet and queries the Peeps contract at `0x383a7b0488756b5618f4ce2bcbc608ad48f09a57`
2. **Get Total Supply**: Calls `totalSupply()` to get the number of tokens
3. **Get Token URIs**: For each token ID (0 to totalSupply-1), calls `tokenURI(uint256)`
4. **Extract Token IDs**: Parses the URIs to extract the actual token IDs (e.g., from `https://api.peeps.club/peep/18089409297514631661.json` extracts `18089409297514631661`)
5. **Compare and Delete**: Compares local files against the official list and deletes any files that aren't official
6. **Preserve Associated Files**: When deleting a JSON file, also deletes the corresponding PNG and SVG files

## Example Output

```
2024-01-15 10:30:15,123 - INFO - Connected to Ethereum mainnet via https://eth-mainnet.g.alchemy.com/v2/demo
2024-01-15 10:30:15,123 - INFO - Contract address: 0x383a7b0488756b5618f4ce2bcbc608ad48f09a57
2024-01-15 10:30:15,456 - INFO - Total supply: 10000
2024-01-15 10:30:15,789 - INFO - Found 10000 official token IDs
2024-01-15 10:30:16,012 - INFO - Found 15000 local JSON files
2024-01-15 10:30:16,234 - INFO - Files to delete: 5000
2024-01-15 10:30:16,456 - INFO - Deleted: 1.json
2024-01-15 10:30:16,456 - INFO - Deleted: 1.png
2024-01-15 10:30:16,456 - INFO - Deleted: 1.svg
...
2024-01-15 10:30:45,123 - INFO - 
Cull completed!
2024-01-15 10:30:45,123 - INFO - Deleted JSON files: 5000
2024-01-15 10:30:45,123 - INFO - Deleted PNG files: 5000
2024-01-15 10:30:45,123 - INFO - Deleted SVG files: 5000
2024-01-15 10:30:45,123 - INFO - Total file groups deleted: 5000
```

## Safety Features

- **Dry Run Mode**: Always test with `--dry-run` first to see what would be deleted
- **Comprehensive Logging**: Every operation is logged for transparency
- **Error Handling**: Network and contract errors are handled gracefully
- **File Association**: Automatically handles associated PNG and SVG files

## Troubleshooting

### Common Issues

**"Failed to connect to Ethereum RPC"**

- Check your internet connection
- Try a different RPC endpoint with `--rpc-url`
- The default endpoint is free but may have rate limits

**"Contract function calls failing"**

- Verify the contract address is correct
- Check that the contract is deployed on mainnet
- Ensure the RPC endpoint supports contract calls

**"No files found to delete"**

- This is normal if all your local files are official
- Check that the `--peep-dir` path is correct
- Verify that JSON files exist in the directory

### RPC Endpoints

The script uses a free Alchemy endpoint by default. For production use, consider:

- **Alchemy**: https://www.alchemy.com/ (free tier available)
- **Infura**: https://infura.io/ (free tier available)
- **QuickNode**: https://www.quicknode.com/ (paid)
- **Your own node**: Run your own Ethereum node

## Dependencies

- `web3>=6.0.0`: Ethereum Python library
- `requests>=2.25.0`: HTTP library for API calls

## License

This script is provided as-is for educational and practical use.
