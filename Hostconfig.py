#!/usr/bin/python3
import socket, subprocess,sys, datetime
from time import sleep
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from broadcast import broadcast
from ast import literal_eval as mtuple
from sendhost import sendhost
from UpdateNameSpace import updatenamespace
import logmsg
from time import time as stamp


def config(leaderip, *bargs):
 rebootme = 0
 arglist = bargs[0]
 #arglist = {'ipaddr': '10.11.11.123', 'ipaddrsubnet': '24', 'id': '0', 'user': 'admin', 'name': 'dhcp32502'}
 queuethis('Hostconfig','running',arglist)
 enpdev='enp0s8'
 needreboot=False
 for key in arglist:
  if arglist[key] == -1:
   arglist[key] = '-1'
 with open('/root/Hostconfig','w') as f:
  f.write(str(arglist)+'\n')
 myhost=socket.gethostname()
 ######### changing alias ###############
 if 'alias' in arglist:
  queuethis('Hostconfig_alias','running',arglist['user'])
  oldarg = str(get(leaderip, 'alias/'+arglist['name'])[0])
  logmsg.sendlog(leaderip, 'HostManual1st5','info',arglist['user'],oldarg, arglist['alias'])
  allhosts = get(leaderip, 'ActivePartner','--prefix')
  put(leaderip, 'alias/'+arglist['name'],arglist['alias'])
  put(leaerip, 'sync/alias/Add_'+arglist['name']+'_'+arglist['alias'].replace('_',':::').replace('/',':::')+'/request','alias_'+str(stamp()))
  put(leaderip, 'sync/alias/Add_'+arglist['name']+'_'+arglist['alias'].replace('_',':::').replace('/',':::')+'/request/'+myhost,'alias_'+str(stamp()))
  logmsg.sendlog(leaderip, 'HostManual1su5','info',arglist['user'],oldarg, arglist['alias'])
  queuethis('Hostconfig_alias','running',arglist['user'])
######### changing cluster address ###############
 if 'cluster' in arglist:
  queuethis('Hostconfig_cluster','running',arglist['user'])
  oldarg = str(get(leaderip, 'namespace/mgmtip')[0])
  logmsg.sendlog(leaderip,'HostManual1st7','info',arglist['user'],oldarg,arglist['cluster'])
#  broadcasttolocal('namespace/mgmtip',arglist['cluster'])
  if myhost == leader:
   updatenamespace(arglist['cluster'],oldarg)
  put(leaderip, 'sync/namespace/Add_'+'namespace::mgmtip_'+arglist['cluster']+'/request','namespace_'+str(stamp()))
  put(leaderip, 'sync/namespace/Add_'+'namespace::mgmtip_'+arglist['cluster']+'/request/'+myhost,'namespace_'+str(stamp()))
  put(leaderip, 'namespace/mgmtip',arglist['cluster'])
  logmsg.sendlog(leaderip, 'HostManual1su7','info',arglist['user'],oldarg,arglist['cluster'])
  queuethis('Hostconfig_cluster','finish',arglist['user'])

############ changing user password ###############
 if 'password' in arglist:
  print('changing password')
  queuethis('ChangeUserPass','running',arglist['user'])
  #broadcasttolocal('userhash/'+arglist['username'],arglist['password'])
  logmsg.sendlog(leaderip, 'Unlin1012','info',arglist['user'],arglist['username'])
  cmdlinep=['/TopStor/encthis.sh',arglist['username'],arglist['password']]
  encthis=subprocess.run(cmdlinep,stdout=subprocess.PIPE).stdout.decode('utf-8').split('_result')[1]
  put(leaderip, 'usershash/'+arglist['username'], encthis)
  cmdlinep=['/TopStor/UnixChangePass',arglist['username'],arglist['user']]
  result=subprocess.run(cmdlinep,stdout=subprocess.PIPE)
  put(leaderip, 'sync/passwd/UnixChangePass_'+arglist['username']+'_'+arglist['user']+'/request','passwd_'+str(stamp()))
  put(leaderip, 'sync/passwd/UnixChangePass_'+arglist['username']+'_'+arglist['user']+'/request/'+myhost,'passwd_'+str(stamp()))
#  broadcast('UserPassChange','/TopStor/pump.sh','UnixChangePass',arglist['password'],arglist['username'],arglist['user'])
  queuethis('ChangeUserPass','finish',arglist['user'])
############ changing time zone ###############
 if 'tz' in arglist:
  queuethis('Hostconfig_tzone','running',arglist['user'])
  oldarg = str(get(leaderip, 'tz/'+myhost)[0])
  argtz = arglist['tz'].split('%')[1]
  logmsg.sendlog(leaderip, 'HostManual1st10','info',arglist['user'],oldarg, argtz)
  put(leaderip, 'tz/'+leader,arglist['tz'])
  put(leaderip, 'sync/tz/HostManualConfigTZ_'+'_'+arglist['tz']+'/request','tz_'+str(stamp()))
  logmsg.sendlog(leaderip 'HostManual1su10','info',arglist['user'], oldarg, argtz)
  queuethis('Hostconfig_tzone','finish',arglist['user'])
########### changing ntp server ###############
 if 'ntp' in arglist:
  queuethis('Hostconfig_ntp','running',arglist['user'])
  oldarg = str(get(leaderip, 'ntp/'+myhost)[0])
  logmsg.sendlog(leaderip, 'HostManual1st9','info',arglist['user'],oldarg, arglist['ntp'])
  put(leaderip, 'ntp/'+leader,arglist['ntp'])
  put(leaderip, 'sync/ntp/HostManualconfigNTP_'+'_'+arglist['ntp']+'/request','ntp_'+str(stamp()))
  logmsg.sendlog(leaderip, 'HostManual1su9','info',arglist['user'],oldarg, arglist['ntp'])
  queuethis('Hostconfig_ntp','finish',arglist['user'])
########### changing dns  ###############
 if 'dnsname' in arglist:
  queuethis('Hostconfig_dns','running',arglist['user'])
  oldargname = str(get(leaderip, 'dnsname/'+myhost)[0])
  oldargsearch = str(get(leaderip, 'dnssearch/'+myhost)[0])
  if arglist['dnsname'] == "":
   arglist['dnsname'] = oldargname
  if arglist['dnssearch'] == "":
   arglist['dnssearch'] = oldargsearch
  logmsg.sendlog(leaderip, 'HostManual1st13','info',arglist['user'],oldargname, oldargsearch, arglist['dnsname'],arglist['dnssearch'])
  put(leaderip, 'dnsname/'+leader,arglist['dnsname'])
  put(leaderip, 'dnssearch/'+leader,arglist['dnssearch'])
  put(leaderip, 'sync/dns/HostManualconfigDNS'+'_'+arglist['dnsname']+'_'+arglist['dnssearch']+'/request','dns_'+str(stamp()))
  logmsg.sendlog(leaderip, 'HostManual1su13','info',arglist['user'],oldargname, oldargsearch, arglist['dnsname'],arglist['dnssearch'])
  queuethis('Hostconfig_dns','finish',arglist['user'])
 
########### changing gateway  ###############
 if 'gw' in arglist:
  queuethis('Hostconfig_gw','running',arglist['user'])
  oldarg = str(get(leaderip, 'gw/'+myhost)[0])
  logmsg.sendlog(leaderip, 'HostManual1st11','info',arglist['user'],oldarg, arglist['gw'])
  put(leaderip, 'gw/'+leader,arglist['gw'])
  put(leaderip, 'sync/gw/HostManualconfigGW_'+'_'+arglist['gw']+'/request','gw_'+str(stamp()))
  logmsg.sendlog(leaderip, 'HostManual1su11','info',arglist['user'],oldarg, arglist['gw'])
  queuethis('Hostconfig_gw','finish',arglist['user'])
 ############# changing configured  ###############
 if 'configured' in arglist:
  print('chaning configured status')
  queuethis('Hostconfig_cf','running',arglist['user'])
  if 'yes' in arglist['configured']:
   logmsg.sendlog(leaderip, 'HostManual1st12','info',arglist['user'])
  else:
   logmsg.sendlog(leaderip, 'HostManual2st12','info',arglist['user'])
  cmdline=['/TopStor/HostManualconfigCF',arglist['configured']]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if 'yes' in arglist['configured']:
   logmsg.sendlog(leaderip, 'HostManual1su12','info',arglist['user'])
  else:
   logmsg.sendlog(leaderip, 'HostManual2su12','info',arglist['user'])
  queuethis('LocalManualConfig.py','stop',bargs[-1])
  rebootme=1
 ########## changing box address ###############
 if 'ipaddr' in arglist:
  print('changin the ipaddress of the node')
  queuethis('Hostconfig_ip','running',arglist['user'])
  oldipaddr = str(get(leaderip, 'ready/'+arglist['name'])[0])
  oldipsubnet= str(get(leaderip, 'ipaddrsubnet/'+arglist['name'])[0])
  logmsg.sendlog(leaderip, 'HostManual1st6','info',arglist['user'],str(oldipaddr)+'/'+str(oldipsubnet),arglist['ipaddr']+'/'+arglist['ipaddrsubnet'])
  if '-1' in str(oldipsubnet):
   oldipsubnet = '-1_.'
  logmsg.sendlog(leaderip, 'HostManual1su6','info',arglist['user'], str(oldipaddr)+'/'+str(oldipsubnet),arglist['ipaddr']+'/'+arglist['ipaddrsubnet'])
  rebootme = 2
######################################
############# need to reboot  ###############
 if rebootme > 0:
  print('sending reboot')
  sendip = get(leaderip, 'ready/'+arglist['name'])[0]
  if rebootme == 2:
   z=['/TopStor/pump.sh','rebootme', 'ipchange', oldipaddr, oldipsubnet, arglist['ipaddr'], arglist['ipaddrsubnet']]
  else:
   z=['/TopStor/pump.sh','rebootme', 'now']
  queuethis('Hostconfig_cf','finish',arglist['user'])
  msg={'req': 'Pumpthis', 'reply':z}
  for x in range(10):
   x =+1
   sendhost(sendip, str(msg),'recvreply',myhost)
   sleep(10)

 queuethis('Hostconfig','finish',arglist['user'])

 return 1






if __name__=='__main__':
 leaderip = sys.argv[1]
 #arg = {'username': 'admin', 'password': 'YousefNadody', 'token': '4f3223c155ca50d13ae975ea18e930bc', 'response': 'admin', 'user': 'admin'}
 arg = {'dnsname': '10.11.11.11', 'dnssearch': 'qstor.com', 'id': '0', 'user': 'admin', 'name': 'dhcp14895', 'token': 'e9b77595837168e6f0ce77f6cbc8137e', 'response': 'admin'}
 arg = {'alias': 'Repli_1', 'ipaddr': '10.11.11.245', 'ipaddrsubnet': '24', 'cluster': '10.11.11.249/24', 'tz': 'Kuwait%(GMT+03!00)_Kuwait^_Riyadh^_Baghdad', 'id': '0', 'user': 'admin', 'name': 'dhcp28109', 'token': '73616fae666891c5f420f63c6317b1ba', 'response': 'admin'}
 config(arg)

#{'cluster': '10.11.11.250/24', 'tz': 'Kuwait%(GMT+03!00)_Kuwait^_Riyadh^_Baghdad', 'id': '0', 'user': 'admin', 'name': 'dhcp32570', 'token': '501ef1257322d1814125b1e16af95aa9', 'response': 'admin'}

