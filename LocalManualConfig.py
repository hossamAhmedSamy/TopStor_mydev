#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import logmsg
def config(*bargs):
 with open('/root/HostManualconfigtmp2','w') as f:
  f.write('bargs:'+str(bargs)+'\n')
 with open('/TopStordata/Hostprop.txt') as f:
  oldbarg=f.read()
 oldbarg=oldbarg.replace('"','').replace('{','').replace('}','').replace(',',' ')
 oldarg=oldbarg.split()
 arg=str(bargs[0]).split()
 change=[]
 owner=''
 msg={}
 for x in arg[:-1]:
  if x not in oldarg:
   change.append(x)
  if 'hostname' in x:
    x=x.split(':')
    owner=x[1]
 if len(change) < 1: 
  return
 logmsg.sendlog('HostManual1002','info',arg[-1])
 with open('/root/HostManualconfigtmp2','a') as f:
  f.write('change:'+str(change)+'\n')
 return 1

if __name__=='__main__':
 config(*sys.argv[1:])
