#!/bin/sh
fixed=`echo $@ | awk '{print $1}'`
logfile=`echo $@ | awk '{print $2}'`
grep "$fixed" $logfile
