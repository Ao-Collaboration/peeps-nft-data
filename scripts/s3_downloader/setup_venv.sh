#!/bin/bash
# Setup script for S3 downloader virtual environment

set -e

echo "Setting up virtual environment for S3 downloader..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if python3-venv is available
if ! python3 -m venv --help &> /dev/null; then
    echo "Error: python3-venv is not available. Please install it first:"
    echo "  sudo apt install python3-venv"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To use the S3 downloader:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the script:"
echo "   python s3_downloader.py --bucket your-bucket --output ./downloads"
echo ""
echo "3. Deactivate when done:"
echo "   deactivate"
echo ""
