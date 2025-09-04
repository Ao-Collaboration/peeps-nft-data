# S3 Bucket Content Downloader

A Python script to download all content from an S3 bucket with support for concurrent downloads, progress tracking, and various configuration options.

## Features

- **Concurrent Downloads**: Download multiple files simultaneously for faster performance
- **Progress Tracking**: Real-time logging of download progress and statistics
- **Prefix Filtering**: Download only objects matching a specific prefix
- **Dry Run Mode**: List objects without downloading them
- **Error Handling**: Robust error handling with detailed logging
- **Configurable**: Multiple command-line options and environment variable support

## Installation

1. Set up a virtual environment:

```bash
cd scripts/s3_downloader
./setup_venv.sh
```

2. Activate the virtual environment:

```bash
source venv/bin/activate
```

### Configure AWS Credentials

After installation, configure AWS credentials (choose one method):

**Option A: .env file (Recommended)**

```bash
cp .env.example .env
# Edit .env with your actual credentials and bucket name
```

**Option B: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
export S3_BUCKET_NAME=your-bucket-name
```

**Option C: AWS CLI**

```bash
aws configure
```

**Option D: IAM Role** (if running on EC2)

## Usage

### Basic Usage

Download all content from a bucket:

```bash
cd scripts/s3_downloader
source venv/bin/activate

# If bucket is set in .env file:
python s3_downloader.py --output ./downloads

# Or specify bucket explicitly:
python s3_downloader.py --bucket my-bucket-name --output ./downloads
```

### Advanced Usage

Download with specific prefix:

```bash
python s3_downloader.py --bucket my-bucket-name --output ./downloads --prefix images/
```

Dry run to see what would be downloaded:

```bash
python s3_downloader.py --bucket my-bucket-name --output ./downloads --dry-run
```

Download with custom settings:

```bash
python s3_downloader.py \
  --bucket my-bucket-name \
  --output ./downloads \
  --prefix data/ \
  --max-workers 20 \
  --region us-west-2 \
  --verbose
```

### Command Line Options

| Option          | Description                              | Default                |
| --------------- | ---------------------------------------- | ---------------------- |
| `--bucket`      | Name of the S3 bucket                    | S3_BUCKET_NAME env var |
| `--output`      | Local directory to save files (required) | -                      |
| `--region`      | AWS region                               | us-east-1              |
| `--prefix`      | S3 prefix to filter objects              | (empty)                |
| `--max-workers` | Number of concurrent download threads    | 10                     |
| `--dry-run`     | List objects without downloading         | False                  |
| `--verbose`     | Enable verbose logging                   | False                  |

### Environment Variables

| Variable                | Description    | Default   |
| ----------------------- | -------------- | --------- |
| `AWS_ACCESS_KEY_ID`     | AWS access key | -         |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | -         |
| `AWS_DEFAULT_REGION`    | AWS region     | us-east-1 |

## Examples

### Download NFT Metadata

```bash
# Download all NFT metadata from a collection
python s3_downloader.py \
  --bucket nft-metadata-bucket \
  --output ./nft-metadata \
  --prefix metadata/ \
  --max-workers 15
```

### Download Images with Progress

```bash
# Download all images with verbose logging
python s3_downloader.py \
  --bucket peeps-nft-images \
  --output ./images \
  --prefix images/ \
  --verbose \
  --max-workers 20
```

### Test Before Download

```bash
# See what would be downloaded first
python s3_downloader.py \
  --bucket my-bucket \
  --output ./test-download \
  --dry-run \
  --verbose
```

## Output

The script provides detailed logging including:

- Connection status
- Number of objects found
- Download progress for each file
- Final statistics (success/failed counts, total size, time taken)

Example output:

```
2024-01-15 10:30:15,123 - INFO - Successfully connected to S3 bucket: my-bucket
2024-01-15 10:30:15,456 - INFO - Found 150 objects to download
2024-01-15 10:30:15,789 - INFO - Downloaded: images/nft-001.png (245760 bytes)
2024-01-15 10:30:16,012 - INFO - Downloaded: images/nft-002.png (198432 bytes)
...
2024-01-15 10:30:45,123 - INFO -
Download completed!
2024-01-15 10:30:45,123 - INFO - Successfully downloaded: 150 files
2024-01-15 10:30:45,123 - INFO - Failed downloads: 0 files
2024-01-15 10:30:45,123 - INFO - Total size: 45.67 MB
2024-01-15 10:30:45,123 - INFO - Time taken: 29.45 seconds
```

## Error Handling

The script handles various error conditions:

- Invalid AWS credentials
- Bucket not found or access denied
- Network connectivity issues
- Individual file download failures
- Permission errors

Failed downloads are logged but don't stop the overall process.

## Performance Tips

1. **Adjust max-workers**: Increase for faster downloads (but be mindful of AWS rate limits)
2. **Use prefixes**: Filter objects to download only what you need
3. **Test first**: Use `--dry-run` to verify your settings
4. **Monitor logs**: Use `--verbose` to see detailed progress

## Troubleshooting

### Common Issues

**"AWS credentials not found"**

- Ensure AWS credentials are properly configured
- Check environment variables or AWS CLI configuration

**"Bucket not found or access denied"**

- Verify bucket name is correct
- Check IAM permissions for S3 access
- Ensure bucket exists in the specified region

**"Permission denied" errors**

- Check write permissions for the output directory
- Ensure sufficient disk space

**Slow downloads**

- Increase `--max-workers` (but not too high)
- Check network connectivity
- Consider downloading during off-peak hours

## License

This script is provided as-is for educational and practical use.
