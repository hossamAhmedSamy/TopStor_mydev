#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
myhost='run/'+myhost
cmdline=['lsscsi','-i','--size']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
lsscsi=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' in x]
cmdline=['/sbin/zpool','status']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
try:
 zpool=str(result.stdout)[2:][:-3].split('\\n')
 z=[]
 z.append((myhost+'/pool/name',zpool[0].split(':')[1].replace(' ','')))
 z.append((myhost+'/pool/state',zpool[1].split(':')[1].replace(' ','')))
 z.append((myhost+'/pool/scan',zpool[2].split(':')[1]))
 cmdline=['/sbin/zpool','list','-H']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 zlist=str(result.stdout)[2:][:-3].split('\\t')
 z.append((myhost+'/pool/size',zlist[1]))
 z.append((myhost+'/pool/alloc',zlist[2]))
 z.append((myhost+'/pool/empty',zlist[3]))
 z.append((myhost+'/pool/dedup',zlist[7]))
 cmdline=['/sbin/zfs','get','compressratio','-H']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 zlist=str(result.stdout)[2:][:-3].split('\\t')
 z.append((myhost+'/pool/compressratio',zlist[2]))
 print(zlist)
 raid='stripe'
 count=0
 diskc=0
 for c in zpool[7:-1]:
  if c.replace(' ','')=='':
   continue
  if 'scsi' not in c:
   raid=c.split()[1]
   raidstat=c.split()[2]
   count+=1
   z.append((myhost+'/pool/raid/'+str(count)+'/type',raid))
   z.append((myhost+'/pool/raid/'+str(count)+'/status',raidstat))
   diskc=0
  else:
   for l in lsscsi:
    ll=l.split()
    if ll[6] in c.split()[1]:
     diskc=lsscsi.index(l)
     break;
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/uuid',c.split()[1]))
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/status',c.split()[2]))
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/fromhost',ll[3]))
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/size',ll[7]))
 if count==0 and diskc > 0:
  z.append((myhost+'/pool/raid/'+str(count)+'/type',raid))
   
 for c in z:
  cmdline=['./etcdput.py',c[0],c[1]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
except:
 pass  
diskc=0
for cc in lsscsi:
  c=cc.split()
  if c[6] not in str(z):
   diskc=lsscsi.index(cc)
   cmdline=['./etcdput.py',myhost+'/free/disk/'+str(diskc)+'/uuid',c[6]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['./etcdput.py',myhost+'/free/disk/'+str(diskc)+'/fromhost',c[3]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['./etcdput.py',myhost+'/free/disk/'+str(diskc)+'/size',c[7]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)

 
