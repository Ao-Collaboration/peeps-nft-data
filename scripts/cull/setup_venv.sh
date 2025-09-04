#!/bin/bash

# Setup script for Peeps NFT Cull Script
# This script creates a virtual environment and installs dependencies

set -e

echo "Setting up virtual environment for Peeps NFT Cull Script..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the cull script:"
echo "  python cull_script.py --peep-dir ../../peep --dry-run"
echo ""
