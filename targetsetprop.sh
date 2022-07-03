#!/bin/sh
echo $@ > /root/targetsetproptmp
cd /TopStor
poolvol=`echo $@ | awk '{print $1}'`
partnerip=`echo $@ | awk '{print $2}'`
props=`echo $@ | awk '{print $3}' | tr ',' ' ' `
partner=`./etcdget.py Partner --prefix | awk -F'Partner/' '{print $2}' | awk -F"', '" '{print $1}' | awk -F'_Sender' '{print $1}'`
if [ -z $partner ];
then
 exit
fi
echo zfs set $props partner:sender=$partner $poolvol 
zfs set $props partner:sender=$partner $poolvol 
