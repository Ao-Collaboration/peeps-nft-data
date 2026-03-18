# Peeps NFT Data Scripts

This directory contains various scripts for managing Peeps NFT data.

## Scripts Overview

### S3 Downloader (`s3_downloader/`)

A Python script to download all content from an S3 bucket with support for concurrent downloads, progress tracking, and various configuration options.

**Features:**
- Concurrent downloads for faster performance
- Progress tracking and detailed logging
- Prefix filtering and dry run mode
- Robust error handling

**Quick Start:**
```bash
cd s3_downloader
./setup_venv.sh
source venv/bin/activate
python s3_downloader.py --bucket my-bucket --output ./downloads
```

[Full Documentation →](s3_downloader/README.md)

### Cull Script (`cull/`)

A Python script that queries the Ethereum contract to get the official list of Peeps NFT token IDs and removes any local files that aren't part of the official collection.

**Features:**
- Ethereum contract integration
- Smart file detection and removal
- Dry run mode for safety
- Comprehensive logging

**Quick Start:**
```bash
cd cull
./setup_venv.sh
source venv/bin/activate
python cull_script.py --peep-dir ../../peep --dry-run
```

[Full Documentation →](cull/README.md)

### Migrate (`migrate/`)

A Python script to migrate image URLs in JSON metadata files from `api.peeps.club` to `data.peeps.club`.

**Features:**
- Batch update JSON metadata files
- Dry run mode for safety

**Quick Start:**
```bash
cd migrate
python migrate_image_url.py --dry-run  # Preview changes
python migrate_image_url.py            # Apply changes
```

## Directory Structure

```
scripts/
├── README.md                 # This file
├── s3_downloader/           # S3 download functionality
│   ├── s3_downloader.py     # Main download script
│   ├── setup_venv.sh        # Virtual environment setup
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Detailed documentation
├── cull/                    # File culling functionality
│   ├── cull_script.py       # Main cull script
│   ├── setup_venv.sh        # Virtual environment setup
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Detailed documentation
└── migrate/                 # Data migration scripts
    └── migrate_image_url.py # Image URL migration script
```

## Getting Started

1. **Choose the script you need** based on your requirements
2. **Navigate to the script directory** (e.g., `cd s3_downloader` or `cd cull`)
3. **Set up the virtual environment** by running `./setup_venv.sh`
4. **Activate the virtual environment** with `source venv/bin/activate`
5. **Run the script** following the specific documentation

## Common Use Cases

### Downloading NFT Data
Use the S3 downloader to download NFT metadata and images from an S3 bucket.

### Cleaning Up Local Files
Use the cull script to remove non-official files by comparing against the Ethereum contract.

### Migrating Data
Use the migrate script to update image URLs or other data across all JSON files.

## Requirements

Each script has its own virtual environment and dependencies. See the individual README files for specific requirements:

- **S3 Downloader**: Requires AWS credentials and boto3
- **Cull Script**: Requires web3 for Ethereum interaction

## License

These scripts are provided as-is for educational and practical use.