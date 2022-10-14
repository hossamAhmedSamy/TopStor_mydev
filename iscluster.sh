#!/bin/sh
nslookup mynode.leader
if [ $? -eq 0 ];
then
 echo isleader
else
 echo notleader
