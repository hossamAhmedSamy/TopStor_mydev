#!/bin/sh
partner=`echo $@ | awk '{print $1}'`
cd /TopStordata/
mkdir ${partner}_keys 2>/dev/null
cd ${partner}_keys 
rm -rf * 2>/dev/null
ssh-keygen -f $partner -N "" 1>/dev/null
cat ${partner}.pub
