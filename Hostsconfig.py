#!/usr/bin/python3
import subprocess,sys, datetime,socket
from logqueue import queuethis
from etcdgetlocalpy import etcdget as get
from etcdgetlocal import etcdget as getlocal
from ast import literal_eval as mtuple
def getall(*bargs):
 with open('/pacedata/perfmon') as f:
  perfmon=f.read()
 if perfmon:
  queuethis('HostManualconfig.py','running')
  with open('/root/tmp','w') as f:
   f.write('bargs'+str(bargs)+'\n')
 leader = get('leader', '--prefix')[0][0].replace('leader/','')
 hosts = get('ready', '--prefix')
 allhosts= [] 
 hostsdict = dict()
 for host in hosts:
  hostname = host[0].replace('ready/','')
  hostip = host[1]
  if hostname not in leader:
   print('###############')
   print(hostip,hostname)
   print('###############')
   ntp = getlocal(hostip,'ntp/'+hostname)[0]
   tz = getlocal(hostip,'tz/'+hostname)[0]
   gw = getlocal(hostip,'gw/'+hostname)[0]
   dnsname = getlocal(hostip,'dnsname/'+hostname)[0]
   dnssearch = getlocal(hostip,'dnssearch/'+hostname)[0]
   ipaddrsubnet = getlocal(hostip,'hostipsubnet/'+hostname)[0]
   alias = getlocal(hostip,'alias/'+hostname)[0]
   configured = getlocal(hostip,'configured/'+hostname)[0]
  else:
   ntp = get('ntp/'+hostname)[0]
   tz = get('tz/'+hostname)[0]
   gw = get('gw/'+hostname)[0]
   dnsname = get('dnsname/'+hostname)[0]
   dnssearch = get('dnssearch/'+hostname)[0]
   alias = get('alias/'+hostname)[0]
   ipaddrsubnet = get('hostipsubnet/'+hostname)[0]
   configured = get('configured/'+hostname)[0]
  if ipaddrsubnet == -1:
   ipaddrsubnet = 24
  mgmt = get('namespace/mgmtip')[0] 
  allhosts.append({'name':hostname, 'configured':configured, 'alias':alias, 'ipaddr': hostip,'ipaddrsubnet':ipaddrsubnet, 'ntp':ntp, 'tz':tz, 'gw': gw,'dnsname':dnsname, 'dnssearch':dnssearch, 'cluster':mgmt})
  hostsdict[hostname] = { 'configured':configured, 'alias':alias, 'ipaddr': hostip, 'ipaddrsubnet':ipaddrsubnet, 'ntp':ntp, 'tz':tz, 'gw': gw, 'dnsname':dnsname, 'dnssearch':dnssearch, 'cluster':mgmt }

 print(allhosts)
 return hostsdict 

if __name__=='__main__':
 getall(*sys.argv[1:])
