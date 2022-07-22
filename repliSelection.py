#!/bin/python3.6

from time import time as timestamp
from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from getallraids import newraids
from levelthis import levelthis
from copy import deepcopy 
allinfo = {}

def selectPool(volname, volsize):
 pools = allinfo['pools']
 volquota = levelthis(volsize,'G')
 pool = 'nopool'
 poolsize = float('inf')
 host = 'nohost'
 for pol in pools:
  if 'Availability' in pools[pol]['availtype'] and pools[pol]['available'] > volquota and pools[pol]['available'] < poolsize:
   pool = pol
   poolsize = pools[pol]['available']
   host = allinfo['hosts'][pools[pol]['host']]['ipaddress']
 pools = host+':'+pool+'/'+volname
 print(pools)
 return pools 
   
 
def selectVol(volname, snap):
 volinfo = allinfo['volumes']
 snapused=levelthis(snap,'B')
 volumes='initial'
 for vol in volinfo:
  if vol == volname:
   if levelthis(volinfo[vol]['available'],'B') > levelthis(snapused):
    hostip = allinfo['hosts'][volinfo[vol]['host']]['ipaddress']
    volumes = hostip+':'+volinfo[vol]['pool']+'/'+vol
   else:
    volumes='No_vol_Space'
  print(volumes)
  return volumes



if __name__=='__main__':
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volsize = levelthis('960000000000000000000000000K','G')
 snapused = levelthis('1K','G')
 volname = 'lcommon_427522895'
 replivol= selectVol(volname,snapused)
 if 'initial' not in replivol:
  print('result_'+replivol+'result_')
 else:
  print('continuing.....')
  replivol = selectPool(volname,volsize)
  if 'nopool' not in replivol:
   print('result_'+replivol+'result_')
  else:
   print('continuing....')
   newraids = newraids(allinfo['disks'])
   print('newraids', newraids)
   
  
# disks = allinfo['disks']
# raids = newraids(disks)
# print(raids)
 
