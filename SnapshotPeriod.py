#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from broadcast import broadcast as broadcast 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 z=[]
 for x in bargs:
  z.append(x)
 broadcast('PeriodManage',str(z),str(poolfile))
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
