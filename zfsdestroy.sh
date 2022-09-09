#!/bin/sh
echo $@ > /root/zfsdestroytmp
snaps=`echo $@ | sed 's/\,/ \-e /g'`
echo snaps: $snaps
zfs list -t snapshot -o name | grep -e $snaps  | xargs -n 1 zfs destroy -r 
