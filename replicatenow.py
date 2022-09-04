#!/bin/python3.6
import sys, subprocess
from time import time as timestamp, sleep
from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from getallraids import newraids, selectdisks
from pumpkeys import pumpkeys


allinfo = {}
phrase = ''
myclusterip = ''
pport = ''
nodeloc = ''
replitype = ''

def checkpartner(receiver, nodeip, cmd, isnew):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 result=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE)
 response = result.stdout.decode()
 print(result.returncode)
 isopen = 'closed' if result.returncode else 'open'
 if result.returncode and isnew == 'old':
  pumpkeys(nodeip, replitype, pport, phrase)
  count = 0
  while count < 10:
   isopen, response = checkpartner(receiver, nodeip,  cmd, 'new')
   count += 1
   if isopen == 'open':
    count = 11
 return isopen, response 

def replitargetget(receiver, volume, volused, snapshot):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 partnerinfo = get('Partner/'+receiver)[0].split('/')
 replitype = partnerinfo[1]
 pport = partnerinfo[2]
 phrase = partnerinfo[-1]
 myclusterip =  get('namespace/mgmtip')[0].split('/')[0]
 print(replitype, pport, phrase, myclusterip )
 nodesinfo = get('Partnernode/'+receiver,'--prefix')
 print('hi',nodesinfo)
 nodesinfo.append(('hi/hi/'+partnerinfo[0],'hi'))
 for node in nodesinfo:
  nodeip = node[0].split('/')[2]
  nodeloc = 'ssh -oBatchmode=yes -i /TopStordata/'+nodeip+'_keys/'+nodeip+' -p '+pport+' -oStrictHostKeyChecking=no '+nodeip 
  print(nodeloc)
  repliselection = nodeloc+' /TopStor/repliSelection.py '+volume+' '+volused+' '+snapshot
  isopen, response = checkpartner(receiver, nodeip, repliselection, 'old')
  print('>>>>>>>>>>>>>>>>>>>>',isopen)
  if 'open' in isopen:
   break
 response = response.split('result_')[1]
 return nodeip, 'closed' if 'open' not in isopen else response

def replistream(receiver, nodeip, snapshot, nodeowner, poolvol, pool, volume):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 myvol = snapshot.split('@')[0] 
 volumeline = get('volume', volume)[0]
 volumeinfo = volumeline[1].split('/') 
 volip = volumeinfo[7]
 volsubnet = volumeinfo[8]
 volgrps = volumeinfo[4]
 voltype = volumeline[0].split('/')[1]
 cmd = 'zfs get quota '+pool+'/'+volume+' -H'
 print(cmd)
 quota=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE).stdout.decode().split('\t')[2]
 print(quota)
 cmd = nodeloc + ' /TopStor/targetcreatevol.sh '+poolvol+' '+volip+' '+volsubnet+' '+quota+' '+voltype+' '+volgrps
 isopen, response = checkpartner(receiver, nodeip, cmd, 'old')
 if 'problem/@problem' in response:
  print(' a problem creating/using the volume in the remote cluster')
  return
 response = response.split('result_')
 if 'old' in response[1]:
  print('old' )
  print('lastsna',response[3] )
  print('poolvol',response[2]) 
 
 else:
  print('lastsna',response[1] )
  print('lastsna',response[3] )
  print('poolvol',response[2]) 
 return

def repliparam(snapshot, receiver):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = snapshot.split('/')[1].split('@')[0]
 pool = snapshot.split('/')[0]
 snapshot = snapshot.split('@')[1]
 volused = str(allinfo['volumes'][volume]['referenced'])
 snapused = '0' 
 
 nodeip, selection = replitargetget(receiver, volume, volused, snapshot)
 if selection == 'closed':
  print('no node is open for replicaiton in the '+receiver)
  return 'closed'
 if 'No_vol_space' in str(selection):
  print('No space in the receiver: '+receiver)
  return 'No_Space'
 nodeowner = selection.split(':')[0]
 poolvol = selection.split(':')[1]
 replistream(receiver, nodeip, snapshot, nodeowner, poolvol, pool, volume)
 return 'result_'+volume, volused, snapshot+'result_'



if __name__=='__main__':
 result = repliparam(*sys.argv[1:])
   
  
# disks = allinfo['disks']
# raids = newraids(disks)
# print(raids)
 
