backup.sh 

#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup_folder_name>"
  exit 1
fi

BACKUP_FOLDER_NAME=$1  
BACKUP_DIR="/TopStordata/$BACKUP_FOLDER_NAME"  
TARGET_DIR="/TopStordata"
ZIPFILE="$TARGET_DIR/$BACKUP_FOLDER_NAME.zip"  

mkdir -p "$BACKUP_DIR"

cp -r /TopStor "$BACKUP_DIR"
cp -r /pace "$BACKUP_DIR"
cp -r /Topstorweb "$BACKUP_DIR"

cd $TARGET_DIR
zip -r "$ZIPFILE" "$BACKUP_FOLDER_NAME"

echo "Backup created at $ZIPFILE with structure under $BACKUP_FOLDER_NAME."
