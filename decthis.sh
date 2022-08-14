#!/bin/sh
username=`echo $@ | awk '{print $1}'`;
password=`echo $@ | awk '{print $2}'`;
decthis=`echo "$password" | openssl enc -e -d -base64 -aes-256-ctr -nopad -nosalt -k '#skMe22'$username`
echo _result${decthis}_result
