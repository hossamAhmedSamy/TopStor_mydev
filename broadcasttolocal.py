#!/bin/python3.6
import sys
from etcdget import etcdget as get
from etcdputlocal import etcdput as putlocal 

def broadcasttolocal(*args):
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  putlocal(k[1],args[0],args[1])

if __name__=='__main__':
 broadcasttolocal(*sys.argv[1:])
