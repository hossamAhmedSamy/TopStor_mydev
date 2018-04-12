#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
myhost='run/'+myhost
cmdline=['/sbin/zpool','status']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
try:
 zpool=str(result.stdout)[2:][:-3].split('\\n')
 z=[]
 z.append((myhost+'/pool/name',zpool[0].split(':')[1].replace(' ','')))
 z.append((myhost+'/pool/state',zpool[1].split(':')[1].replace(' ','')))
 z.append((myhost+'/pool/scan',zpool[2].split(':')[1]))
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
   diskc+=1
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/uuid',c.split()[1]))
   z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/status',c.split()[2]))
 if count==0 and diskc > 0:
  z.append((myhost+'/pool/raid/'+str(count)+'/type',raid))
   
 for c in z:
  cmdline=['./etcdput.py',c[0],c[1]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
except:
 pass  
cmdline=['lsscsi','-i']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
lsscsi=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' in x]
diskc=0
for c in lsscsi:
  c=c.split()
  if c[6] not in str(z):
   diskc+=1
   cmdline=['./etcdput.py',myhost+'/free/disk/'+str(diskc)+'/uuid',c[6]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['./etcdput.py',myhost+'/free/disk/'+str(diskc)+'/fromhost',c[3]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)

 
