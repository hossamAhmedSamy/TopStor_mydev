#!/bin/sh
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
docker run -v /pdhcp1807130007/nefo:/pdhcp1807130007/nefo -v /etc/exports.nefo:/etc/exports:ro --cap-add SYS_ADMIN -p 2049:2049  -p 2049:2049/udp  -p 32765:32765 -p 32765:32765/udp -p 111:111 -p 111:111/udp -p 32767:32767 -p 32767:32767/udp --name nfs 10.11.11.124:5000/nfs
