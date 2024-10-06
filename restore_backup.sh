#!/bin/bash

BACKUP_FOLDER=$1

BACKUP_PATH="/TopStordata/$BACKUP_FOLDER"

if [ -d "$BACKUP_PATH" ]; then
    echo "Backup folder '$BACKUP_FOLDER' found at $BACKUP_PATH."
else
    echo "Error: Backup folder '$BACKUP_FOLDER' not found in /TopStordata."
    exit 1
fi

if [ -d "$BACKUP_PATH/TopStor" ] && [ -d "$BACKUP_PATH/pace" ] && [ -d "$BACKUP_PATH/topstorweb" ]; then
    echo "TopStor, pace, and topstorweb found in the backup folder."
else
    echo "Error: TopStor, pace, or topstorweb not found in the backup folder."
    exit 1
fi

CURRENT_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_CURRENT_PATH="/TopStordata/original_backup_$CURRENT_DATE"

echo "Creating a backup of the current directories at $BACKUP_CURRENT_PATH..."
mkdir -p "$BACKUP_CURRENT_PATH"

if [ -d "/TopStor" ]; then
    mv -i /TopStor "$BACKUP_CURRENT_PATH/"
    echo "Moved current TopStor to $BACKUP_CURRENT_PATH."
fi

if [ -d "/pace" ]; then
    mv -i /pace "$BACKUP_CURRENT_PATH/"
    echo "Moved current pace to $BACKUP_CURRENT_PATH."
fi

if [ -d "/topstorweb" ]; then
    mv -i /topstorweb "$BACKUP_CURRENT_PATH/"
    echo "Moved current topstorweb to $BACKUP_CURRENT_PATH."
fi

if [ ! -d "/TopStor" ] && [ ! -d "/pace" ] && [ ! -d "/topstorweb" ]; then
    echo "All directories successfully moved, starting the replacement process..."
else
    echo "Error: Moving the directories failed, aborting replacement."
    exit 1
fi

echo "Replacing current directories with the backup versions using rsync..."
rsync -av --delete "$BACKUP_PATH/TopStor/" /TopStor/
rsync -av --delete "$BACKUP_PATH/pace/" /pace/
rsync -av --delete "$BACKUP_PATH/topstorweb/" /topstorweb/

echo "Replacement complete."

sync
sync
sync

echo "Backup replacement process finished successfully."
