#!/usr/bin/python3
import sys, subprocess
from allphysicalinfo import getall 
from etcdgetlocalpy import etcdget as get
from pumpkeys import pumpkeys


allinfo = {}
phrase = ''
myclusterip = ''
pport = ''
nodeloc = ''
replitype = 'Receiver'

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
 myclusterip =  get('leaderip')[0]
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

def replistream(receiver, nodeip, snapshot, nodeowner, poolvol, pool, volume, csnaps):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 myvol = pool+'/'+volume 
 mysnaps = sorted(allinfo['volumes'][volume]['snapshots'], key= lambda x : x.split('.')[-1], reverse=True)
 oldsnap = 'noold'
 for snap in mysnaps:
  if snap in csnaps:
   oldsnap = snap
   break
 volumeline = get('volume', volume)[0]
 volumeinfo = volumeline[1].split('/') 
 volip = volumeinfo[7]
 volsubnet = volumeinfo[8]
 volgrps = volumeinfo[4]
 voltype = volumeline[0].split('/')[1]
 cmd = '/usr/sbin/zfs get quota '+myvol+' -H'
 quota=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE).stdout.decode().split('\t')[2]
 cmd = nodeloc + ' /TopStor/targetcreatevol.sh '+poolvol+' '+volip+' '+volsubnet+' '+quota+' '+voltype+' '+volgrps+' '+oldsnap
 isopen, response = checkpartner(receiver, nodeip, cmd, 'old')
 response = response.split('result_')
 if oldsnap == 'noold':
  response[1] = 'newvol/@new'
 if 'problem/@problem' in response[1]:
  print(' a problem creating/using the volume in the remote cluster')
  return
 elif 'newvol/@new' in response[1]:
  #print('./sendzfs.sh new '+ myvol+'@'+snapshot +' '+ poolvol +' '+ nodeloc.replace(' ','%%'))
  cmd = './sendzfs.sh new '+ myvol+'@'+snapshot +' '+ poolvol +' '+ nodeloc.replace(' ','%%')
 else:
  #cmd = './sendzfs.sh old '+myvol+'@'+lastsnap+' '+myvol+'@'+snapshot+' '+poolvol+' '+nodeloc
  cmd = './sendzfs.sh old '+myvol+'@'+oldsnap+' '+myvol+'@'+snapshot+' '+response[2]+' '+nodeloc.replace(' ','%%')
  print('./sendzfs.sh old '+myvol+'@'+oldsnap+' '+myvol+'@'+snapshot+' '+response[2]+' '+nodeloc.replace(' ','%%'))
 stream = subprocess.run(cmd.split(' '),stdout=subprocess.PIPE).stdout.decode()
 print('streaming: ',stream)
 print('start checking csnaps')
 csnaps = csnaps.split(',')
 cmd = '/usr/sbin/zfs list -t snapshot -o name'
 mysnaps=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE).stdout.decode()
 destroy = ''
 for snap in csnaps:
  if snap == 'csnaps':
   continue
  if snap not in mysnaps:
   destroy = destroy + poolvol+'@'+snap+',' 
 if len(destroy) > 5:
  cmd = nodeloc + ' /TopStor/zfsdestroy.sh '+destroy[:-1]
  with open('/root/destroynow','w') as f:
    f.write(cmd+'\n')
  checkpartner(receiver, nodeip, cmd, 'old')
 print('end checking csnaps')
 return stream

def repliparam(snapshot, receiver):
 global allinfo, phrase, myclusterip, pport, nodeloc, replitype
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = snapshot.split('/')[1].split('@')[0]
 pool = snapshot.split('/')[0]
 snapshot = snapshot.split('@')[1].replace(' ','')
 volused = str(allinfo['volumes'][volume]['referenced'])
 snapused = '0' 
 
 nodeip, selection = replitargetget(receiver, volume, volused, snapshot)
 if selection == 'closed':
  print('no node is open for replication in the '+receiver)
  return 'closed'
 if 'No_vol_space' in str(selection):
  print('No space in the receiver: '+receiver)
  return 'No_Sppue'
 print('selection',selection)
 nodeowner = selection.split(':')[0]
 poolvol = selection.split(':')[1].split('@')[0]
 try:
  csnaps = selection.split('@')[1]
 except:
  csnaps = 'noold'
 result = replistream(receiver, nodeip, snapshot, nodeowner, poolvol, pool, volume, csnaps)
 if 'fail' in result:
  cmd = '/usr/sbin/zfs destroy -r '+' '+pool+'/'+volume+'@'+snapshot 
 else:
  cmd = '/usr/sbin/zfs set partner:receiver='+receiver.split('_')[0]+' '+pool+'/'+volume+'@'+snapshot
 subprocess.run(cmd.split(' '),stdout=subprocess.PIPE).stdout.decode()
 #return _'+volume, volused, snapshot+'result_'
 return result



if __name__=='__main__':
 result = repliparam(*sys.argv[1:])
