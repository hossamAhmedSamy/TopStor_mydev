#!/bin/python3.6
from logqueue import queuethis
from etcdgetpy import etcdget as get
from ast import literal_eval as mtuple
import subprocess, copy
from levelthis import levelthis
import sys


def getsnapperiods(voldict):
 periodsdict = dict()
 snapperiods = get('Snapperiod','--prefix') 
 for per in snapperiods:
  leftper = per[0].split('/')
  rightper = per[1].split('/')
  vol = leftper[3]
  voldict[vol]['snapperiod'].append(leftper[4])
  periodsdict[leftper[4]] = dict()
  periodsdict[leftper[4]]['host']=voldict[vol]['host']
  periodsdict[leftper[4]]['pool']=voldict[vol]['pool']
  periodsdict[leftper[4]]['volume']=vol
  periodsdict[leftper[4]]['periodtype']=leftper[1]
  periodsdict[leftper[4]]['id']=leftper[4]
  if 'Minutely' in leftper[1]: 
   periodsdict[leftper[4]]['keep']=rightper[4].split('.')[1]
   periodsdict[leftper[4]]['every']=rightper[4].split('.')[2]
  elif 'Hourly' in leftper[1]: 
   periodsdict[leftper[4]]['keep']=rightper[4].split('.')[1]
   periodsdict[leftper[4]]['sminute']=rightper[4].split('.')[2]
   periodsdict[leftper[4]]['every']=rightper[4].split('.')[3]
  elif 'Weekly' in leftper[1]: 
   periodsdict[leftper[4]]['keep']=rightper[3].split('.')[1]
   hr=rightper[3].split('.')[2]
   ampm = 'AM'
   if int(hr) > 12 :
    hr = int(hr) - 12
    ampm = 'PM'
   mint=rightper[3].split('.')[3]
   periodsdict[leftper[4]]['stime']=str(hr)+':'+str(mint)+' '+ampm
   periodsdict[leftper[4]]['every']=rightper[3].split('.')[4].split('%')[0]
 return (periodsdict,voldict)

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
   pool['used'] = levelthis(pool['used'])
   pool['available'] = levelthis(pool['available'])
   pool['alloc'] = levelthis(pool['alloc'])
   pool['empty'] = levelthis(pool['empty'])
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
     disk['size'] = levelthis(disk['size'])
     raiddisks.append(disk['name'])
     disksdict[disk['name']] = disk.copy()
   poolvolumes = []
   poolsdict[pool['name']]['volumes'] = poolvolumes
   for volume in pool['volumes']:
    volume['used'] = levelthis(volume['used'])
    volume['quota'] = levelthis(volume['quota'])
    volume['usedbysnapshots'] = levelthis(volume['usedbysnapshots'],'M')
    poolvolumes.append(volume['name'])
    thevolume = volume.copy()
    #echo /pace/etcdput.py volumes/CIFS/$myhost/$DG/$name $DG/$name/no/yes/$writev/administrator/yes >> /root/volchange
    thevolume.pop('snapshots',None)
    volumesnapshots = []
    volumesnapperiods = []
    for snapshot in volume['snapshots']:
     snapshot['used'] = levelthis(snapshot['used'],'M')
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
 snapperiodsdict = dict()
 snapperiodsdict, volumesdict = getsnapperiods(volumesdict) 
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
 return {'hosts':hostsdict, 'pools':poolsdict, 'raids':raidsdict, 'disks':disksdict, 'volumes':volumesdict, 'snapshots':snapshotsdict, 'snapperiods':snapperiodsdict}

 
if __name__=='__main__':
 alldsks = get('host','current')
 print('hihihih')
 getall(alldsks, *sys.argv[1:])
