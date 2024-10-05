#!/bin/bash

# Set variables
TOPSTOR_DIR="/root/TopStor"
TARGET_DIR="/TopStordata"
ZIPFILE="$TARGET_DIR/TopStor_$(date +%Y%m%d).zip"
PASSWORD="TopStor_$(date +%Y%m%d)"

# Ensure the target directory exists
mkdir -p $TARGET_DIR

# Create the zip file with a password and preserve directory structure
zip -rP $PASSWORD $ZIPFILE $TOPSTOR_DIR

# Print success message
echo "TopStor directory compressed to $ZIPFILE with password: $PASSWORD"
