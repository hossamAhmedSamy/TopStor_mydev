#!/usr/bin/python3
import subprocess,sys, datetime
import json
from etcdgetlocalpy import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from etcddellocal import etcddel as dellocal 

def delbroadcastlocal(*args):
 knowns=[]
 knowninfo=get(args[0],'known','--prefix')
 for k in knowninfo:
  dellocal(k[1],args[1],args[2])

if __name__=='__main__':
 delbroadcastlocal(*sys.argv[1:])
