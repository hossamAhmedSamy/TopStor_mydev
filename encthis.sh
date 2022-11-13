#!/bin/sh
username=`echo $@ | awk '{print $1}'`
userpass=`echo $@ | awk '{print $2}'`
encthis=`echo "$userpass" | openssl enc -d -e  -base64 -aes-256-ctr  -pbkdf2 -nopad -k '#skMe22'$username`
echo _result${encthis}_result
