#!/bin/python3.6

from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from levelthis import levelthis


def getmirror(single,group):
 mirror = dict() 
 for size in single:
  if len(single[size]) >= group:
   mirror[size] = size 
 return mirror

def getraid(single,group,parity):
 theraid = dict()
 for size in single:
  dif = len(single[size]) - group
  base = round(size*(group -parity ),2)
  count = 0 
  while dif >= 0:
   theraid[base] = {'disk':size, 'diskcount': count+group }
   base += size
   dif -= 1 
   count += 1
 return theraid

allraids ={'raid5':{'parity':1, 'group':3 } , 'raid6':{ 'parity':2, 'group':4},
           'raid6+':{'parity':3, 'group':5} }

def newraids(diskdict):
 allsizes = dict() 
 single = dict() 
 allsizes['single'] = single
 for disk in diskdict:
  if 'free' in diskdict[disk]['raid']:
   if diskdict[disk]['size'] not in single:
    single[diskdict[disk]['size']] = []
   single[diskdict[disk]['size']].append(disk)
 for raid in allraids:
  theraid = getraid(single,allraids[raid]['group'],allraids[raid]['parity']) 
  if len(theraid) > 0:
   allsizes[raid] = theraid.copy()
 theraid = getmirror(single,2)
 if len(theraid) > 0:
  allsizes['mirror'] = theraid
 print(allsizes)
 return allsizes

if __name__=='__main__':
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 disks = allinfo['disks']
 newraids(disks)
 
