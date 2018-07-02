#!/bin/python3.6
import subprocess
from etcdput import etcdput as put
cmdline='/sbin/zpool status'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
y=str(result)[2:][:-3].replace('\\t','').split('\\n')
with open("tmp") as f:
 y=f.read()
y=y.split('\n')
cmdline='/bin/lsscsi -is'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
lsscsi=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
freepool=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
raidtypes=['mirror','raidz','stripe']
raid2=['log','cache','spare']
zpool=[]
for a in y:
 b=a.split()
 if "pdhc" in a and  'pool' not in a:
  raidlist=[]
  zdict={}
  zdict={ 'name':b[0], 'status':b[1], 'raidlist': raidlist }
  zpool.append(zdict)
 elif any(raid in a for raid in raidtypes):
  disklist=[]
  zdict={ 'name':b[0], 'status':b[1],'disklist':disklist }
  raidlist.append(zdict)
 elif any(raid in a for raid in raid2):
  disklist=[]
  zdict={ 'name':b[0], 'status':'NA','disklist':disklist }
  raidlist.append(zdict)
 elif 'scsi' in a:
   diskid='-1'
   host='-1'
   size='-1' 
   for lss in lsscsi:
    z=lss.split()
    if z[6] in b[0]:
     diskid=lsscsi.index(lss)
     host=z[3].split('-')[1]
     size=z[7]
     freepool.remove(lss)
     break
   zdict={'name':b[0], 'status':b[1],'id': diskid, 'host':host, 'size':size}
   disklist.append(zdict)
 else:
   zdict={'name':'na','status':a}
   #zpool.append(zdict)
if len(freepool) > 0:
 raidlist=[]
 zdict={ 'name':'free', 'status':'free', 'raidlist': raidlist }
 zpool.append(zdict)
 disklist=[]
 zdict={ 'name':'free', 'status':'free','disklist':disklist }
 raidlist.append(zdict)
 for lss in freepool:
  z=lss.split()
  diskid=lsscsi.index(lss)
  host=z[3].split('-')[1]
  size=z[7]
  zdict={'name':z[6], 'status':'free','id': diskid, 'host':host, 'size':size}
  disklist.append(zdict)
print(zpool)
put('myhost/current',str(zpool))
