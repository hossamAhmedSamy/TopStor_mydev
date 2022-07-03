#!/bin/python3.6
import sys
from time import time as timestamp, sleep
from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from getallraids import newraids, selectdisks
from levelthis import levelthis
from sendhost import sendhost
from copy import deepcopy 
from socket import gethostname as hostname

allinfo = {}
myhost = hostname()

def selectDG(volname , volsize):
 global allinfo, myhost
 posraids = newraids(allinfo['disks'])
 raidname = 'noraid'
 raidsize = float('inf')
 createdpool = 'nopool'
 raidhosts = 'nohost' 
 for raid in posraids:
  if ('mirror' or 'raid') in raid: 
   for raidsz in posraids[raid]:
    if raidsz > volsize and raidsz < raidsize:
     raidsize = raidsz 
     raidname = raid
     raidhosts = posraids[raid][raidsz]['hosts']
 dgsinfo = {'raids':allinfo['raids'], 'pools':allinfo['pools'], 'disks':allinfo['disks']}
 dgsinfo['newraid'] = posraids
 if len(dgsinfo['newraid']) == 0 or 'noraid' in raidname:
  return 'No_vol_Space'
 data = {}
 data['redundancy'] = raidname
 data['useable'] = raidsize
 data['user'] = 'system'
 if data['useable'] not in dgsinfo['newraid'][data['redundancy']]:
  keys = list(dgsinfo['newraid'][data['redundancy']].keys())
  keys.append(float(data['useable']))
  keys.sort()
  diskindx = keys.index(float(data['useable'])) + 1
  if diskindx == len(keys):
   diskindx = len(keys) - 2 
  data['useable'] = keys[diskindx]
 disks =  dgsinfo['newraid'][data['redundancy']][data['useable']]
 if 'single' in data['redundancy']:
  selecteddisks= disks
 else:
  selecteddisks = selectdisks(disks,dgsinfo['newraid']['single'],allinfo['disks'])
 owner = allinfo['disks'][selecteddisks[0]]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 diskstring = ''
 for dsk in selecteddisks:
  diskstring += dsk+":"+dsk[-5:]+" "
 if 'single' in data['redundancy']:
  datastr = 'Single '+data['user']+' '+owner+" "+selecteddisks[0]+" "+selecteddisks[0][-5:]+" nopool "+data['user']+" "+owner
 elif 'mirror' in data['redundancy']:
  datastr = 'mirror '+data['user']+' '+owner+" "+diskstring+"nopool "+data['user']+" "+owner
 elif 'volset' in data['redundancy']:
  datastr = 'stripeset '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 elif 'raid5' in data['redundancy']:
  datastr = 'parity '+data['user']+' '+owner+" "+diskstring
 elif 'raid6plus' in data['redundancy']:
  datastr = 'parity3 '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 elif 'raid6' in data['redundancy']:
  datastr = 'parity2 '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 cmndstring = '/TopStor/pump.sh DGsetPool '+datastr+' '+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 sendhost(ownerip, str(msg),'recvreply',myhost)
 counter = 120
 while counter > 0:
  counter -= 1
  sleep(10)
  alldsks = get('host','current')
  allinfo = getall(alldsks)
  allinfo = getall(alldsks)
  newpool = allinfo['disks'][selecteddisks[0]]['pool']
  if 'ree' not in newpool:
   createdpool = newpool
   counter = -10 
 host = allinfo['pools'][createdpool]['host']
 hostip = allinfo['hosts'][host]['ipaddress']
 result = hostip+':'+createdpool+'/'+volname
 return result
  
 
  
def selectPool(volname, volsize):
 pools = allinfo['pools']
 volquota = levelthis(volsize,'G')
 pool = 'No_vol_space'
 poolsize = float('inf')
 host = 'No_vol_space'
 for pol in pools:
  if 'pree' not in pol and 'Availability' in pools[pol]['availtype'] and levelthis(pools[pol]['available']) > volquota and pools[pol]['available'] < poolsize:
   pool = pol
   poolsize = pools[pol]['available']
   host = allinfo['hosts'][pools[pol]['host']]['ipaddress']
 pools = host+':'+pool+'/'+volname
 return pools 
   
 
def selectVol(volname, volsize):
 volinfo = allinfo['volumes']
 volumes='No_vol_Space'
 for vol in volinfo:
  if vol == volname:
   if levelthis(volinfo[vol]['available'],'B') > levelthis(volsize,'B') - levelthis(volinfo[vol]['used'],'B'):
    hostip = allinfo['hosts'][volinfo[vol]['host']]['ipaddress']
    volumes = hostip+':'+volinfo[vol]['pool']+'/'+vol
   else:
    volumes='No_vol_Space'
 return volumes



if __name__=='__main__':
 volname = sys.argv[1]
 volsize = float(sys.argv[2])
 snapshot = sys.argv[3]
 #snapused = levelthis(sys.argv[4])
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 #volsize = sys.argvlevelthis('96K','G')
 #snapused = levelthis('1K','G')
 #volname = 'common_427522895'
 print('check existing volumes.....')
 replivol= selectVol(volname,volsize)
 if 'No_vol_Space' in replivol:
  print('continuing to check existing pool.....')
  replivol = selectPool(volname,volsize)
  if 'No_vol_Space' in replivol:
   print('continuing to create a pool....')
   replivol = selectDG(volname,volsize)
 print('result_'+replivol+'result_')

   
  
# disks = allinfo['disks']
# raids = newraids(disks)
# print(raids)
 
