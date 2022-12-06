#!/bin/sh
export ETCDCTL_API=3
cd /TopStor/
prot=`echo $@ | awk '{print $1}'`

if [[ $prot == 'cifs' ]];
then
 head -n 2 /pdhcp*/smb.* | grep CIFS | grep SUMMARY | grep active |  awk '{print $4}' 2>/dev/null
 exit
fi
if [[ $prot == 'home' ]];
then
 head -n 2 /pdhcp*/smb.* | grep HOME | grep SUMMARY | grep active | awk -F'HOME ' '{print $2}' 2>/dev/null
 exit
fi
if [[ $prot == 'iscsi' ]];
then
 head -n 2 /pdhcp*/iscsi.* | grep ISCSI | grep SUMMARY | grep active | awk -F'ISCSI ' '{print $2}' 2>/dev/null
 exit
fi
