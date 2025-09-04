# Peeps NFT Data

This repository contains the metadata for the Peeps Club NFTs.

## Links

* [Peeps Club Website](https://peeps.club)
* [Opensea Collection](https://opensea.io/collection/peeps-club)

## Scripts

This repository includes several utility scripts for managing Peeps NFT data:

* **[S3 Downloader](scripts/s3_downloader/README.md)** - Download all content from an S3 bucket with concurrent downloads and progress tracking
* **[Cull Script](scripts/cull/README.md)** - Query the Ethereum contract to get official token IDs and remove non-official local files

### Quick Start

**Download NFT data:**
```bash
cd scripts/s3_downloader
./setup_venv.sh
source venv/bin/activate
python3 s3_downloader.py --bucket your-bucket --output ./downloads
```

**Clean up local files:**
```bash
cd scripts/cull
./setup_venv.sh
source venv/bin/activate
python3 cull_script.py --peep-dir ../../peep --dry-run
```

For detailed documentation, see the [Scripts Overview](scripts/README.md).
