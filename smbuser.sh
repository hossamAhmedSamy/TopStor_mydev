#!/bin/sh
(echo $2; echo $2) | /usr/bin/smbpasswd -s -a $1 
