#!/bin/sh
cores=`lscpu  | grep 'CPU(s):' | grep -v NUMA | awk '{print $2}'`
loadavg=`uptime | awk '{print $NF'}`
echo $cores $loadavg
