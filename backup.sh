#!/bin/bash

TOPSTOR_DIR="/root/TopStor"
TARGET_DIR="/TopStordata"
ZIPFILE="$TARGET_DIR/TopStor_$(date +%Y%m%d).zip"
PASSWORD="TopStor_$(date +%Y%m%d)"

mkdir -p $TARGET_DIR

zip -rP $PASSWORD $ZIPFILE $TOPSTOR_DIR

echo "TopStor directory compressed to $ZIPFILE with password: $PASSWORD"
