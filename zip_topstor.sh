#!/bin/bash

# Check if a folder name argument is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup_folder_name>"
  exit 1
fi

# Set variables
BACKUP_FOLDER_NAME=$1  # Custom folder name from the command line
BACKUP_DIR="/TopStordata/$BACKUP_FOLDER_NAME"  # Use the provided folder name
TARGET_DIR="/TopStordata"
ZIPFILE="$TARGET_DIR/$BACKUP_FOLDER_NAME.zip"  # The zip file will be named using the provided folder name

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Copy the directories you want to backup into the backup folder
cp -r /TopStor "$BACKUP_DIR"
cp -r /pace "$BACKUP_DIR"
cp -r /Topstorweb "$BACKUP_DIR"

# Compress the backup folder into a zip file
cd $TARGET_DIR
zip -r "$ZIPFILE" "$BACKUP_FOLDER_NAME"

# Print success message
echo "Backup created at $ZIPFILE with structure under $BACKUP_FOLDER_NAME."
