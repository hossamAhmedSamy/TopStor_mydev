#!/bin/python3.6
import subprocess, socket
from os import listdir
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels 
from os.path import getmtime

def getpoolstoimport():
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline() 
 if '1' in perfmon:
  queuethis('putzpoolfound.py','start','system')
 myhost=socket.gethostname()
 sitechange=0
 readyhosts=get('ready','--prefix')
 currentpools=str(get('host','--prefix'))
 cmdline='/sbin/zpool import'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 sty=str(result)[2:][:-3].replace('\\t','').split('\\n')
 cmdline='/bin/lsscsi -is'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 lsscsi=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 freepool=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 periods=get('Snapperiod','--prefix')
 raidtypes=['mirror','raidz','stripe']
 availraid=['mirror','raidz']
 raid2=['log','cache','spare']
 zpool=[]
 spaces=-2
 raidlist=[]
 disklist=[]
 lpools=[]
 ldisks=[]
 ldefdisks=[]
 linusedisks=[]
 lfreedisks=[]
 lsparedisks=[]
 lhosts=set()
 phosts=set()
 lraids=[]
 lvolumes=[]
 lsnapshots=[]
 poolsstatus=[]
 x=list(map(chr,(range(97,123))))
 drives=';sd'.join(x).split(';')
 drives[0]='sd'+drives[0]
 cmdline=['fdisk','-l']
 cdisks=subprocess.run(cmdline,stdout=subprocess.PIPE)
 drives=[ x for x in drives if x in str(cdisks)]
 for a in sty:
  b=a.split()
  if len(b) > 0:
   b.append(b[0])
   if any(drive in str(b[0]) for drive in drives):
    for lss in lsscsi:
     if any('/dev/'+b[0] in lss for drive in drives):
      b[0]='scsi-'+lss.split()[6]
      
  if "pdhc" in str(b) and  'pool' not in str(b):
   if b[0] in currentpools:
    continue
   disklist=[]
   zdict={}
   diskhosts = set()
   rdict={}
   ddict={}
   availtype = ''
   poolsstatus.append(('pools/'+b[0],myhost))
   zdict={ 'name':b[0],'changeop':b[1], 'status':b[1],'currenthosts': diskhosts}
   zpool.append(zdict)
  elif 'scsi' in str(b) or 'disk' in str(b) or '/dev/' in str(b) or (len(b) > 0 and 'sd' in b[0]  and len(b[0]) < 5):
   diskid='-1'
   host='-1'
   size='-1' 
   devname='-1'
   disknotfound=1
   if  len(a.split('scsi')[0]) < (spaces+2) or (len(raidlist) < 1 and len(zpool)> 0):
    disklist=[]
    b[1] = 'NA'
   for lss in lsscsi:
    z=lss.split()
    if z[6] in b[0] and len(z[6]) > 3 and 'OFF' not in b[1] :
     diskid=lsscsi.index(lss)
     host=z[3].split('-')[1]
     lhosts.add(host)
     phosts.add(host)
     size=z[7]
     devname=z[5].replace('/dev/','')
     freepool.remove(lss)
     disknotfound=0
     break
   if disknotfound == 1:
     diskid=0
     host='-1'
     size='-1'
   changeop=b[1]
   if host=='-1':
    raidlist[len(raidlist)-1]['changeop']='Warning'
    zpool[len(zpool)-1]['changeop']='Warning'
    changeop='Removed'
    sitechange=1
   diskhosts.add(host)
   ddict={'name':b[0],'actualdisk':b[-1], 'changeop':changeop,'pool':zdict['name'],'status':b[1],'id': str(diskid), 'host':host, 'size':size,'devname':devname}
   disklist.append(ddict)
 queuethis('putzpoolfound.py','stop','system')
 print(zpool)
 return zpool

if __name__=='__main__':
 getpoolstoimport()
