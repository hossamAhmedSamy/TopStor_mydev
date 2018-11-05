#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from etcdputlocal import etcdput as putlocal 

def broadcasttolocal(*args):
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  putlocal(k[1],args[0],args[1])

if __name__=='__main__':
 broadcasttolocal(*sys.argv[1:])
