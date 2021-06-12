#!/bin/python3.6
from logqueue import queuethis
from etcdgetpy import etcdget as get
from ast import literal_eval as mtuple
import subprocess, copy
import sys

def getall(*args):
 alldsks = args[0]
 hostsdict = dict()
 poolsdict = dict()
 raidsdict = dict()
 volumesdict = dict()
 disksdict = dict()
 snapshotsdict = dict()
 snapperiodsdict = dict()
 allvols = []
 vols = get('volumes','--prefix')
 for vol in vols:
  voldict = dict()
  if len(vol[1].split('/')) < 7:
   continue
  voldict = {'name': vol[1].split('/')[1], 'pool': vol[1].split('/')[0], 'groups': '', 'ipaddress': '', 'Subnet': '', 'prot': '', 'fullname': '', 'host': '', 'creation': '', 'time': '', 'used': 0, 'quota': 0, 'usedbysnapshots': 0, 'refcompressratio': '1.0x', 'snapperiod': [], 'snapshots': []}
  if vol[0].split('/')[1] == 'CIFS' or vol[0].split('/')[1] == 'HOME' :
   voldict['groups'] = vol[1].split('/')[4]
   voldict['ipaddress'] = vol[1].split('/')[7] 
   voldict['Subnet'] = vol[1].split('/')[8]
   voldict['prot'] = vol[0].split('/')[1]
   print(voldict['prot'])
   volumesdict[voldict['name']] = voldict.copy()
  elif vol[0].split('/')[1] == 'NFS':
   voldict['groups'] = vol[1].split('/')[8]
   voldict['ipaddress'] = vol[1].split('/')[9] 
   voldict['Subnet'] = vol[1].split('/')[10]
   voldict['prot'] = 'NFS'
   volumesdict[voldict['name']] = voldict.copy()
 for alldsk in alldsks:
  host = alldsk[0].split('/')[1]
  pools = mtuple(alldsk[1])
  hostpools = []
  hostip = get('ActivePartners/'+host)[0]
  hostsdict[host] = {'name': host,'ipaddress': hostip, 'pools': hostpools }
  for pool in pools:
   hostpools.append(pool['name'])
   thepool = pool.copy()
   thepool.pop('raidlist',None)
   thepool.pop('volumes',None)
   poolraids = []
   poolsdict[pool['name']] = dict()
   poolsdict[pool['name']] = thepool.copy() 
   poolsdict[pool['name']]['raids'] = poolraids
   for raid in pool['raidlist']:
    poolraids.append(raid['name'])
    theraid = raid.copy()
    theraid.pop('disklist',None)
    raiddisks = []
    raidsdict[raid['name']] = dict()
    raidsdict[raid['name']] = theraid.copy()
    raidsdict[raid['name']]['disks'] = raiddisks
    for disk in raid['disklist']:
     raiddisks.append(disk['name'])
     disksdict[disk['name']] = disk.copy()
   poolvolumes = []
   poolsdict[pool['name']]['volumes'] = poolvolumes
   for volume in pool['volumes']:
    poolvolumes.append(volume['name'])
    thevolume = volume.copy()
    #echo /pace/etcdput.py volumes/CIFS/$myhost/$DG/$name $DG/$name/no/yes/$writev/administrator/yes >> /root/volchange
    thevolume.pop('snapshots',None)
    volumesnapshots = []
    volumesnapperiods = []
    for snapshot in volume['snapshots']:
     volumesnapshots.append(snapshot['name'])
     snapshotsdict[snapshot['name']] = snapshot.copy() 
    if 'snapperiods' in volume:
     thevolume.pop('snapperiod',None)
     for snapperiod in volume['snapperiod']:
      volumesnapperiods.append(snapperiod['name'])
      snapperiodsdict[snapperiod['name']] = snapperiod.copy() 
    if volume['name'] not in volumesdict:
     volumesdict[volume['name']] = dict()
     volumesdict[volume['name']] = thevolume.copy()
    else:
     volumesdict[volume['name']].update(thevolume) 
    volumesdict[volume['name']]['snapshots'] = volumesnapshots
    volumesdict[volume['name']]['snapperiod'] = volumesnapperiods
 '''
 print('#############')
 print('hosts',hostsdict)
 print('#############')
 print('pools',poolsdict)
 print('#############')
 print('raids',raidsdict)
 print('#############')
 print('disks',disksdict)
 print('#############')
 print('volumes',volumesdict)
 print('#############')
 print('snapshots',snapshotsdict)
 print('#############')
 print('snapperiods',snapperiodsdict) 
 '''
 print('volumes',volumesdict)
 return {'hosts':hostsdict, 'pools':poolsdict, 'raids':raidsdict, 'disks':disksdict, 'volumes':volumesdict, 'snapshots':snapshotsdict, 'snapperiods':snapperiodsdict}

 
if __name__=='__main__':
 alldsks = get('host','current')
 getall(alldsks, *sys.argv[1:])
