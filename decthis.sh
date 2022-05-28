#!/bin/sh
echo "$@" | openssl enc -e -d -base64 -aes-256-ctr -nopad -nosalt -k '#skMe22shomakaher'
