#!/usr/bin/python3
import subprocess,sys, datetime,socket
from logqueue import queuethis
import json
from etcdput import etcdput as put 
import logmsg
def do(data):
 name=data['name']
 user=data['user']
 queuethis('AddHost','running',user)
 logmsg.sendlog('AddHostst01','info',user,name)
 put('allowedPartners',name)
 queuethis('AddHost','stop',user)

if __name__=='__main__':
 do(*sys.argv[1:])
