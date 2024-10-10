#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup_folder_name>"
  exit 1
fi

BACKUP_FOLDER_NAME=$1  
BACKUP_DIR="/TopStordata/$BACKUP_FOLDER_NAME"  
TARGET_DIR="/TopStordata"
TARFILE="$TARGET_DIR/$BACKUP_FOLDER_NAME.tar.gz"

# Spinner function
spin() {
  local -a marks=( '|' '/' '-' '\' )
  while :; do
    for mark in "${marks[@]}"; do
      printf '\r[%s] Creating backup, please wait...' "$mark"
      sleep 0.1
    done
  done
}

# Run spinner in the background
spin &
SPIN_PID=$!

tar -czf "$TARFILE" -C / TopStor pace topstorweb

kill "$SPIN_PID" > /dev/null 2>&1
printf '\nBackup created at %s.\n' "$TARFILE"
