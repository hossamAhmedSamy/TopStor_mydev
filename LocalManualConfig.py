#!/bin/python3.6
import subprocess,sys, datetime
from etcdget import etcdget as get
from etcdput import etcdput as put
from ast import literal_eval as mtuple
import logmsg
def config(*bargs):
 enpdev='enp0s8'
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
######### changing name ###############
 if 'name' in change:
  logmsg.sendlog('HostManual1st5','info',arg[-1],change['oldname'],change['name'])
  put('alias/'+owner,change['name'])
  logmsg.sendlog('HostManual1su5','info',arg[-1],change['oldname'],change['name'])
######### changing cluster address ###############
 if 'mgmtip' in change:
  if 'mgmtsubnet' in change:
   subnet=change['subnet']
   oldsubnet=change['oldsubnet']
  else:
   subnet=oldsubnet=24
   for y in oldarg:
    if 'mgmtsubnet' in y:
     y=y.split(':')
     subnet=oldsubnet=y[1]
  logmsg.sendlog('HostManual1st7','info',arg[-1],change['oldmgmtip']+'/'+oldsubnet,change['mgmtip']+'/'+subnet)
  cmdline=['/TopStor/HostManualconfigNameSpace',change['mgmtip'],change['oldmgmtip'],subnet,oldsubnet]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su7','info',arg[-1],change['oldmgmtip']+'/'+oldsubnet,change['mgmtip']+'/'+subnet)
######### changing box address ###############
 if 'addr' in change:
  if 'subnet' in change:
   subnet=change['subnet']
   oldsubnet=change['oldsubnet']
  else:
   subnet=oldsubnet=24
   for y in oldarg:
    if 'subnet' in y:
     y=y.split(':')
     subnet=oldsubnet=y[1]
     
  logmsg.sendlog('HostManual1st6','info',arg[-1],change['oldaddr']+'/'+oldsubnet,change['addr']+'/'+subnet)
  cmdline=['/TopStor/HostManualconfigCC',change['addr'],change['oldaddr'],subnet,oldsubnet]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su6','info',arg[-1],change['oldaddr']+'/'+oldsubnet,change['addr']+'/'+subnet)
#####################################################
 return 1

if __name__=='__main__':
 config(*sys.argv[1:])
