#!/bin/bash

# Function to display a spinner during long-running tasks
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

BACKUP_FOLDER=$1

# Path to the compressed backup file (assuming .tar.gz format)
BACKUP_FILE="/TopStordata/$BACKUP_FOLDER.tar.gz"

# Path to the temporary directory for extraction
TEMP_DIR="/TopStordata/tempdata"

# Check if the backup file exists
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup file '$BACKUP_FOLDER.tar.gz' found at /TopStordata."
else
    echo "Error: Backup file '$BACKUP_FOLDER.tar.gz' not found in /TopStordata."
    exit 1
fi

CURRENT_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_CURRENT_PATH="/TopStordata/original_backup_$CURRENT_DATE"

echo "Creating a backup of the current directories at $BACKUP_CURRENT_PATH..."
mkdir -p "$BACKUP_CURRENT_PATH"

# Move current directories to the backup location
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

# Ensure directories were moved before proceeding
if [ ! -d "/TopStor" ] && [ ! -d "/pace" ] && [ ! -d "/topstorweb" ]; then
    echo "All directories successfully moved, starting the extraction process..."
else
    echo "Error: Moving the directories failed, aborting extraction."
    exit 1
fi

# Create temporary directory for extraction
mkdir -p "$TEMP_DIR"

# Extract the tar.gz backup file into the temporary directory
echo "Extracting backup file '$BACKUP_FILE' to $TEMP_DIR..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR/"

# Verify if extraction was successful by checking the presence of required directories in tempdata
if [ -d "$TEMP_DIR/TopStor" ] && [ -d "$TEMP_DIR/pace" ] && [ -d "$TEMP_DIR/topstorweb" ]; then
    echo "Backup contents successfully extracted, starting replacement..."
else
    echo "Error: Failed to extract TopStor, pace, or topstorweb from the backup."
    exit 1
fi

# Start rsync operations with a spinner
echo "Replacing current directories with backup versions. Please wait..."

rsync -a --delete "$TEMP_DIR/TopStor/" /TopStor/ &
spinner $!
rsync -a --delete "$TEMP_DIR/pace/" /pace/ &
spinner $!
rsync -a --delete "$TEMP_DIR/topstorweb/" /topstorweb/ &
spinner $!

echo "Replacement complete."

# Cleanup: remove the temporary extraction directory and the original backup directory
rm -rf "$TEMP_DIR"
rm -rf "$BACKUP_CURRENT_PATH"

sync
sync
sync

echo "Backup replacement process finished successfully, and cleanup is done."
