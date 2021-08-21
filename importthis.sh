#!/bin/sh
/sbin/zpool import $@ -m
if [ $? -eq 0 ];
then
 echo ok
else
 echo failed 
fi
