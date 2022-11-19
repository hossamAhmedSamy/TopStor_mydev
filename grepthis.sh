#!/bin/sh
fixed=`echo $@ | awk '{print $1}'`
sev=`echo $@ | awk '{print $2}'`
logfile=`echo $@ | awk '{print $3}'`
grep "$fixed" $logfile | grep $sev
