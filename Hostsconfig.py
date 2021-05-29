#!/bin/python3.6
import subprocess,sys, datetime,socket
from logqueue import queuethis
from etcdget import etcdget as get
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
 for host in hosts:
  hostname = host[0].replace('ready/','')
  hostip = host[1]
  if hostname not in leader:
   ntp = getlocal(hostip,'ntp/'+hostname)[0]
   tz = getlocal(hostip,'tz/'+hostname)[0]
   gw = getlocal(hostip,'gw/'+hostname)[0]
   alias = getlocal(hostip,'alias/'+hostname)[0]
  else:
   ntp = get('ntp/'+hostname)[0]
   tz = get('tz/'+hostname)[0]
   gw = get('gw/'+hostname)[0]
   alias = get('alias/'+hostname)[0]
  mgmt = get('namespace/mgmtip')[0] 
  allhosts.append({'name':hostname,'alias':alias, 'ip': hostip, 'ntp':ntp, 'tz':tz, 'gw': gw, 'cluster':mgmt})

 print(allhosts)
 return allhosts 

if __name__=='__main__':
 getall(*sys.argv[1:])
