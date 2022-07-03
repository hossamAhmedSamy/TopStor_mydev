#!/bin/sh
echo $@ > /root/targetcreatevol
cd /TopStor

owner=`hostname`
pool=`echo $@ | awk '{print $1}' | awk -F'/' '{print $1}'`
name=`echo $@ | awk '{print $1}' | awk -F'/' '{print $2}'`
ipaddress=`echo $@ | awk '{print $2}'`
Subnet=`echo $@ | awk '{print $3}'`
typep=`echo $@ | awk '{print $4}'`
./creatmyvol.py $owner $pool $name $ipaddress $Subnet $typep 
 
