#!/bin/python3.6
import subprocess,sys, datetime
from etcdget import etcdget as get
from etcdput import etcdput as put
from ast import literal_eval as mtuple
import logmsg
def config(*bargs):
 with open('/root/HostManualconfigtmp2','w') as f:
  f.write('bargs:'+str(bargs)+'\n')
 with open('/TopStordata/Hostprop.txt') as f:
  oldbarg=f.read()
 oldbarg=oldbarg.replace('"','').replace('{','').replace('}','').replace(',',' ')
 oldarg=oldbarg.split()
 arg=bargs
 with open('/root/HostManualconfigtmp2','a') as f:
  f.write('arg:'+str(arg)+'\n')
 change={}
 owner=''
 msg={}
 for x in arg[:-1]:
  if x not in oldarg:
   x=x.split(':')
   change[x[0]]=x[1]
   for y in oldarg:
    if x[0] in y and 'host' not in y:
     y=y.split(':')
     change['old'+x[0]]=y[1]
  if 'hostname' in x:
    x=x.split(':')
    owner=x[1]
 if len(change) < 1: 
  return
 logmsg.sendlog('HostManual1002','info',arg[-1])
 with open('/root/HostManualconfigtmp2','a') as f:
  f.write('change:'+str(change)+'\n')
 if 'name' in change:
  logmsg.sendlog('HostManual1st5','info',arg[-1],change['oldname'],change['name'])
  put('alias/'+owner,change['name'])
  logmsg.sendlog('HostManual1su5','info',arg[-1],change['oldname'],change['name'])
 return 1

if __name__=='__main__':
 config(*sys.argv[1:])
