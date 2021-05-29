#!/bin/python3.6
import socket, subprocess,sys, datetime
from logqueue import queuethis
from etcdget import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from broadcast import broadcast
from ast import literal_eval as mtuple
from sendhost import sendhost
from UpdateNameSpace import updatenamespace
import logmsg
def config(*bargs):
 queuethis('Hostconfig.py','running',bargs[-1])
 enpdev='enp0s8'
 needreboot=False
 arglist = dict()
 for barg in bargs:
  arglist[barg.split('=')[0]] = barg.split('=')[1]
 with open('/root/Hostconfig','w') as f:
  f.write(str(arglist)+'\n')
 #rglist = {'name': 'dhcp32502', 'tz': 'Kirit%(GMT-10!00)_Hawaii', 'id': '0', 'user': 'mezo'} 
 leaderinfo = get('leader','--prefix')[0]
 leader = leaderinfo[0].replace('leader/','')
 leaderip = leaderinfo[1]
 myhost=socket.gethostname()
 ######### changing alias ###############
 if 'alias' in arglist:
  oldarg = get('alias/'+myhost)[0]
  if arglist['alias'] != oldarg:
   logmsg.sendlog('HostManual1st5','info',arglist['user'],oldarg,arglist['alias'])
   put('alias/'+arglist['name'],arglist['alias'])
   broadcasttolocal('alias/'+arglist['name'],arglist['alias'])
   logmsg.sendlog('HostManual1su5','info',arglist['user'],oldarg,arglist['alias'])
######### changing cluster address ###############
 if 'cluster' in arglist:
  oldarg = get('namespace/mgmtip')[0]
  logmsg.sendlog('HostManual1st7','info',arglist['user'],oldarg,arglist['cluster'])
  if myhost == leader:
   updatenamespace(arglist['cluster'])
  else:
   z=['/TopStor/pump.sh','UpdateNameSpace.py', arglist['cluster'],oldarg]
   msg={'req': 'Pumpthis', 'reply':z}
   sendhost(leaderip, str(msg),'recvreply',myhost)
  broadcasttolocal('namespace/mgmtip',arglist['cluster'])
  logmsg.sendlog('HostManual1su7','info',arglist['user'],oldarg,arglist['cluster'])
############ changing time zone ###############
 if 'tz' in arglist:
  print('iamhere')
  oldarg = get('tz/'+myhost)[0]
  argtz = arglist['tz'].split('%')[1]
  logmsg.sendlog('HostManual1st10','info',arglist['user'],oldarg, argtz)
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   print('host',hostname)
   put('tz/'+hostname,arglist['tz'])
   broadcasttolocal('tz/'+hostname,arglist['tz'])
  broadcast('HostManualConfigTZ','/TopStor/pump.sh','HostManualconfigTZ')
  logmsg.sendlog('HostManual1su10','info',arglist['user'], oldarg, argtz)
######################################



 exit()
 oldbarg=oldbarg.replace('"','').replace('{','').replace('}','').replace(',',' ')
 oldarg=oldbarg.split()
 arg=bargs
 with open('/root/HostManualconfigtmp2','w') as f:
  f.write('arg:'+str(arg)+'\n')
 with open('/root/HostManualconfigtmp2','a') as f:
  f.write('oldarg:'+str(oldarg)+'\n')
 change={}
 owner=''
 msg={}
 setarg=set(arg[:-1])
 setold=set(oldarg)
 diff=setarg-setold
 print(diff)
 newchange=list(diff) 
 print(newchange)
 for x in newchange:
  kvx=x.split(':')
  change[kvx[0]]=kvx[1]
  for y in oldarg:
   kvy=y.split(':')
   if kvy[0]==kvx[0]:
    change['old'+kvy[0]]=kvy[1]
 
 if len(change) < 1: 
  queuethis('LocalManualConfig.py','stop_cancel',bargs[-1])
  return
 logmsg.sendlog('HostManual1002','info',arg[-1])
 with open('/root/HostManualconfigtmp2','a') as f:
  f.write('change:'+str(change)+'\n')
 '''
 change = {'tz': 'Kuw@@(GMT+03!00)_Kuwait@_Riyadh@_Baghdad', 'oldtz': '@@_Africa/Cairo_(EET@_+0200)', 'name': 'stor11', 'oldname': 'stor0', 'mgmtip': '192.168.9.12', 'oldmgmtip': '192.168.8.24', 'ntp': '1.asia.pool.ntp.org', 'oldntp': '0.asia.pool.ntp.org'}
 '''
####### changing data address ###############
 if 'dataip' in change:
  if 'dataipsubnet' in change:
   subnet=change['dataipsubnet']
   oldsubnet=change['olddataipsubnet']
  else:
   subnet=oldsubnet=24
   for y in oldarg:
    if 'dataipsubnet' in y:
     y=y.split(':')
     subnet=oldsubnet=y[1]
  logmsg.sendlog('HostManual1st8','info',arg[-1],change['olddataip']+'/'+oldsubnet,change['dataip']+'/'+subnet)
  cmdline=['/TopStor/HostManualconfigDataIP',change['dataip'],change['olddataip'],subnet,oldsubnet]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su8','info',arg[-1],change['olddataip']+'/'+oldsubnet,change['dataip']+'/'+subnet)
########## changing ntp server ###############
 if 'ntp' in change:
  logmsg.sendlog('HostManual1st9','info',arg[-1],change['oldntp'],change['ntp'])
  cmdline=['/TopStor/HostManualconfigNTP.py',change['ntp']]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su9','info',arg[-1],change['oldntp'],change['ntp'])
########### changing gateway  ###############
 if 'gw' in change:
  logmsg.sendlog('HostManual1st11','info',arg[-1],change['oldgw'],change['gw'])
  cmdline=['/TopStor/HostManualconfigGW.py',change['gw']]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su11','info',arg[-1],change['oldgw'],change['gw'])
 ############ changing configured  ###############
 if 'configured' in change:
  if 'yes' in change['configured']:
   logmsg.sendlog('HostManual1st12','info',arg[-1])
  else:
   logmsg.sendlog('HostManual2st12','info',arg[-1])
   
  cmdline=['/TopStor/HostManualconfigCF',change['configured']]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if 'yes' in change['configured']:
   logmsg.sendlog('HostManual1su12','info',arg[-1])
  else:
   logmsg.sendlog('HostManual2su12','info',arg[-1])
  needreboot=True
 ######### changing box address ###############
 if 'addr' in change:
  if 'addrsubnet' in change:
   subnet=change['addrsubnet']
   oldsubnet=change['oldaddrsubnet']
  else:
   subnet=oldsubnet=24
   for y in oldarg:
    if 'addrsubnet' in y:
     y=y.split(':')
     subnet=oldsubnet=y[1]
  with open('/root/HostManualconfigtmp2','a') as f:
   f.write('/will/change box address)\n');
  logmsg.sendlog('HostManual1st6','info',arg[-1],change['oldaddr']+'/'+oldsubnet,change['addr']+'/'+subnet)
  cmdline=['/TopStor/HostManualconfigCC',change['addr'],change['oldaddr'],subnet,oldsubnet]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  #cmdline=['/TopStor/rebootme',change['addr'],change['oldaddr'],subnet,oldsubnet]
  #result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('HostManual1su6','info',arg[-1],change['oldaddr']+'/'+oldsubnet,change['addr']+'/'+subnet)
  needreboot=True
####################################################
# cmdline=['/TopStor/HostgetIPs']
 queuethis('LocalManualConfig.py','stop',bargs[-1])
 if needreboot:
  cmdline=['/TopStor/rebootme','now']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  
 return 1

if __name__=='__main__':
 config(*sys.argv[1:])
