#!/usr/bin/python3
import sys
from etcdgetlocalpy import etcdget as get
from etcdputlocal import etcdput as putlocal 

def broadcasttolocal(*args):
 knowns=[]
 knowninfo=get(args[0],'known','--prefix')
 for k in knowninfo:
  putlocal(k[1],args[1],args[2])

if __name__=='__main__':
 broadcasttolocal(*sys.argv[1:])
