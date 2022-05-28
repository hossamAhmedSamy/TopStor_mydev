#!/bin/sh
echo "$@" | openssl enc -d -e  -base64 -aes-256-ctr -nopad -nosalt -k '#skMe22shomakaher'
