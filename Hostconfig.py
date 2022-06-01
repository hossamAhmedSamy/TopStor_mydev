#!/bin/python3.6
import socket, subprocess,sys, datetime
from time import sleep
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
 arglist = bargs[0]
 #arglist = {'ipaddr': '10.11.11.123', 'ipaddrsubnet': '24', 'id': '0', 'user': 'admin', 'name': 'dhcp32502'}
 queuethis('Hostconfig','running',arglist['user'])
 enpdev='enp0s8'
 needreboot=False
 for key in arglist:
  if arglist[key] == -1:
   arglist[key] = '-1'
 with open('/root/Hostconfig','w') as f:
  f.write(str(arglist)+'\n')
 leaderinfo = get('leader','--prefix')[0]
 leader = leaderinfo[0].replace('leader/','')
 leaderip = leaderinfo[1]
 myhost=socket.gethostname()
 ######### changing alias ###############
 if 'alias' in arglist:
  queuethis('Hostconfig_alias','running',arglist['user'])
  oldarg = get('alias/'+myhost)[0]
  logmsg.sendlog('HostManual1st15','info',arglist['user'],oldarg, arglist['alias'])
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   put('alias/'+leader,arglist['alias'])
   broadcasttolocal('alias/'+leader,arglist['ntp'])
  z=['/TopStor/pump.sh','HostManualconfigAlias']
  msg={'req': 'Pumpthis', 'reply':z}
  sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su15','info',arglist['user'],oldarg, arglist['ntp'])
  queuethis('Hostconfig_Alias','finish',arglist['user'])
######### changing cluster address ###############
 if 'cluster' in arglist:
  queuethis('Hostconfig_cluster','running',arglist['user'])
  oldarg = get('namespace/mgmtip')[0]
  logmsg.sendlog('HostManual1st7','info',arglist['user'],oldarg,arglist['cluster'])
  broadcasttolocal('namespace/mgmtip',arglist['cluster'])
  put('namespace/mgmtip',arglist['cluster'])
  if myhost == leader:
   updatenamespace(arglist['cluster'],oldarg)
  else:
   z=['/TopStor/pump.sh','UpdateNameSpace.py', arglist['cluster'],oldarg]
   msg={'req': 'Pumpthis', 'reply':z}
   sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su7','info',arglist['user'],oldarg,arglist['cluster'])
  queuethis('Hostconfig_cluster','finish',arglist['user'])

############ changing user password ###############
 if 'password' in arglist:
  queuethis('ChangeUserPass','running',arglist['user'])
  #broadcasttolocal('userhash/'+arglist['username'],arglist['password'])
  broadcast('UserPassChange','/TopStor/pump.sh','UnixChangePass',arglist['password'],arglist['username'],arglist['user'])
  queuethis('ChangeUserPass','finish',arglist['user'])
############ changing time zone ###############
 if 'tz' in arglist:
  queuethis('Hostconfig_tzone','running',arglist['user'])
  oldarg = get('tz/'+myhost)[0]
  argtz = arglist['tz'].split('%')[1]
  logmsg.sendlog('HostManual1st10','info',arglist['user'],oldarg, argtz)
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   put('tz/'+leader,arglist['tz'])
   broadcasttolocal('tz/'+leader,arglist['tz'])
  z=['/TopStor/pump.sh','HostManualconfigTZ']
  msg={'req': 'Pumpthis', 'reply':z}
  sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su10','info',arglist['user'], oldarg, argtz)
  queuethis('Hostconfig_tzone','finish',arglist['user'])
########### changing ntp server ###############
 if 'ntp' in arglist:
  queuethis('Hostconfig_ntp','running',arglist['user'])
  oldarg = get('ntp/'+myhost)[0]
  logmsg.sendlog('HostManual1st9','info',arglist['user'],oldarg, arglist['ntp'])
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   put('ntp/'+leader,arglist['ntp'])
   broadcasttolocal('ntp/'+leader,arglist['ntp'])
  z=['/TopStor/pump.sh','HostManualconfigNTP']
  msg={'req': 'Pumpthis', 'reply':z}
  sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su9','info',arglist['user'],oldarg, arglist['ntp'])
  queuethis('Hostconfig_ntp','finish',arglist['user'])
########### changing dns  ###############
 if 'dnsname' in arglist:
  queuethis('Hostconfig_dns','running',arglist['user'])
  oldargname = get('dnsname/'+myhost)[0]
  oldargsearch = get('dnssearch/'+myhost)[0]
  if arglist['dnsname'] == "":
   arglist['dnsname'] = oldargname
  if arglist['dnssearch'] == "":
   arglist['dnssearch'] = oldargsearch
  logmsg.sendlog('HostManual1st13','info',arglist['user'],oldargname, oldargsearch, arglist['dnsname'],arglist['dnssearch'])
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   put('dnsname/'+leader,arglist['dnsname'])
   put('dnssearch/'+leader,arglist['dnssearch'])
   broadcasttolocal('dnsname/'+leader,arglist['dnsname'])
   broadcasttolocal('dnssearch/'+leader,arglist['dnssearch'])
  z=['/TopStor/pump.sh','HostManualconfigDNS']
  msg={'req': 'Pumpthis', 'reply':z}
  sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su13','info',arglist['user'],oldargname, oldargsearch, arglist['dnsname'],arglist['dnssearch'])
  queuethis('Hostconfig_dns','finish',arglist['user'])
 
########### changing gateway  ###############
 if 'gw' in arglist:
  queuethis('Hostconfig_gw','running',arglist['user'])
  oldarg = get('gw/'+myhost)[0]
  logmsg.sendlog('HostManual1st11','info',arglist['user'],oldarg, arglist['gw'])
  allhosts = get('ActivePartner','--prefix')
  for host in allhosts:
   hostname = host[0].replace('ActivePartners/','')
   put('gw/'+leader,arglist['gw'])
   broadcasttolocal('gw/'+leader,arglist['gw'])
  z=['/TopStor/pump.sh','HostManualconfigGW']
  msg={'req': 'Pumpthis', 'reply':z}
  sendhost(leaderip, str(msg),'recvreply',myhost)
  logmsg.sendlog('HostManual1su11','info',arglist['user'],oldarg, arglist['gw'])
  queuethis('Hostconfig_gw','finish',arglist['user'])
 ############# changing configured  ###############
 if 'configured' in arglist:
  queuethis('Hostconfig_cf','running',arglist['user'])
  if 'yes' in arglist['configured']:
   logmsg.sendlog('HostManual1st12','info',arglist['user'])
  else:
   logmsg.sendlog('HostManual2st12','info',arglist['user'])
  cmdline=['/TopStor/HostManualconfigCF',arglist['configured']]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if 'yes' in arglist['configured']:
   logmsg.sendlog('HostManual1su12','info',arglist['user'])
  else:
   logmsg.sendlog('HostManual2su12','info',arglist['user'])
  queuethis('LocalManualConfig.py','stop',bargs[-1])
  z=['/TopStor/pump.sh','rebootme', 'now']
  msg={'req': 'Pumpthis', 'reply':z}
  sendip = get('ready/'+arglist['name'])[0]
  queuethis('Hostconfig_cf','finish',arglist['user'])
  for x in range(10):
   x =+1
   sendhost(sendip, str(msg),'recvreply',myhost)
   sleep(10)
 ########## changing box address ###############
 if 'ipaddr' in arglist:
  queuethis('Hostconfig_ip','running',arglist['user'])
  oldipaddr = get('ready/'+arglist['name'])[0]
  oldipsubnet=get('ipaddrsubnet/'+arglist['name'])[0]
  logmsg.sendlog('HostManual1st6','info',arglist['user'],str(oldipaddr)+'/'+str(oldipsubnet),arglist['ipaddr']+'/'+arglist['ipaddrsubnet'])
  if '-1' in str(oldipsubnet):
   oldipsubnet = '-1_.'
  z=['/TopStor/pump.sh','rebootme', 'ipchange', oldipaddr, oldipsubnet, arglist['ipaddr'], arglist['ipaddrsubnet']]
  print('zzzzzzzzzzzzzz',z)
  msg={'req': 'Pumpthis', 'reply':z}
  sendip = get('ready/'+arglist['name'])[0]
  logmsg.sendlog('HostManual1su6','info',arglist['user'], str(oldipaddr)+'/'+str(oldipsubnet),arglist['ipaddr']+'/'+arglist['ipaddrsubnet'])
  queuethis('Hostconfig_ip','finish',arglist['user'])
  for x in range(10):
   x =+1
   sendhost(sendip, str(msg),'recvreply',myhost)
   sleep(10)
######################################
 queuethis('Hostconfig','finish',arglist['user'])

 return 1






if __name__=='__main__':
 config(*sys.argv[1:])
