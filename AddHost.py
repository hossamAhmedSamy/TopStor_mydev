#!/bin/python3.6
import subprocess,sys, datetime,socket
from logqueue import queuethis
import json
from etcdput import etcdput as put 
import logmsg
def setall(*bargs):
 arg=bargs
 name=bargs[-2]
 queuethis('AddHost.py','running',bargs[-1])
 logmsg.sendlog('AddHostst01','info',arg[-1],name)
 put('allowedPartners',name)
 queuethis('AddHost.py','stop_initiated',bargs[-1])

if __name__=='__main__':
 setall(*sys.argv[1:])
