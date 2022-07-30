#!/bin/python3.6
import sys
from etcdget import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from time import time as stamp
from socket import gethostname as hostname
from levelthis import levelthis

myhost=hostname()
def addtrend(vol,size,stamp):
 normsize = str(levelthis(size))
 csizes = get('sizevol/'+vol)[0]
 csizes += '/'+stamp+'-'+normsize
 put('sizevol/'+vol,csizes)
 put('sync/sizevol/'+myhost, str(stamp()))
 broadcasttolocal('sizevol/'+vol,csizes)
 
if __name__=='__main__':
 addtrend(*sys.argv[1:])
