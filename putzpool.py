#!/bin/python3.6
import traceback
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
myhost='run/'+myhost
cmdline=['lsscsi','-i','--size']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
lsscsi=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' in x]
ata=[x for x in str(result.stdout)[2:][:-3].split('\\n') if 'LIO' not in x]
cmdline=['/sbin/zpool','status']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
try:
 zpool=str(result.stdout)[2:][:-3].split('\\n')
 z=[]
 if zpool==['']:
  cmdline=['/pace/etcddel.py',myhost,'--prefix']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  zpool=[':nopool',':nopool',':nopool','nopool','nopool','nopool','nopool','nopool']
 else:
  cmdline=['/sbin/zfs','list','-t','snapshot,filesystem','-o','name,creation,used,quota,usedbysnapshots,refcompressratio,prot:kind','-H']
  vollist=subprocess.run(cmdline,stdout=subprocess.PIPE)
  vollist=[x.split('\\t') for x in str(vollist.stdout)[2:][:-3].split('\\n')]
  snap=[]
  for y in vollist:
   try:
    names=y[0].split('/')
    snap=y[0].split('@')[1]
    thisvol='pool/'+names[0]+'/vol/'+names[1].split('@')[0]+'/snapshot/'+names[1].split('@')[1]+y[6]
    thisvolvalue=y[1]+'/'+y[2]+'/'+y[5]
    print('is a snapshot')
   except:
    try:
     names=y[0].split('/')
     thisvol='pool/'+names[0]+'/vol/'+names[1]+'/'+y[6]
     thisvolvalue=y[3]+'/'+y[2]+'/'+y[4]+'/'+y[5]
     print('is a vol')
    except:
     thisvol='pool/'
     thisvolvalue=y[3]+'/'+y[2]+'/'+y[4]+'/'+y[5]
     print('is a pool')
   z.append((myhost+thisvol,thisvolvalue))
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
  raid='stripe'
  count=0
  diskc=0
  tmpc=6
  for c in zpool[7:-1]:
   if c.replace(' ','')=='':
    continue
   if 'scsi' not in c:
    count+=1
    cc=c.split()
    cc.append(cc[0].replace('\\t','').replace('\\',''))
    cc.append('ONLINE/AVAIL')
    raid=cc[1]
    raidstat=cc[2]
    z.append((myhost+'/pool/raid/'+str(count)+'/type',raid))
    z.append((myhost+'/pool/raid/'+str(count)+'/status',raidstat))
    diskc=0
   else:
    if count==0:
     count+=1
     z.append((myhost+'/pool/raid/'+str(count)+'/type','stripe'))
     raidstat=zpool[1].split(':')[1].replace(' ','')
     z.append((myhost+'/pool/raid/'+str(count)+'/status',raidstat))
    for l in lsscsi:
     ll=l.split()
     if ll[6] in c.split()[1]:
      diskc=lsscsi.index(l)
      if ll[3].split('-')[0] not in str(ata) or ll[7]=='-':
       status='FAULT'
      else:
       status=c.split()[2]
      break;
    z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/uuid',c.split()[1]))
    z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/fromhost',ll[3]))
    z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/size',ll[7]))
    z.append((myhost+'/pool/raid/'+str(count)+'/disk/'+str(diskc)+'/status',status))
  if count==0 and diskc > 0:
   z.append((myhost+'/pool/raid/'+str(count)+'/type',raid))
   
  for c in z:
   cmdline=['/pace/etcdput.py',c[0],c[1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
except Exception as e:
 traceback.print_exc()
 pass  
diskc=0
for cc in lsscsi:
  c=cc.split()
  if c[6] not in str(z):
   print('hi',c)
   diskc=lsscsi.index(cc)
   cmdline=['/pace/etcdput.py',myhost+'/free/disk/'+str(diskc)+'/uuid',c[6]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdput.py',myhost+'/free/disk/'+str(diskc)+'/fromhost',c[3]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcdput.py',myhost+'/free/disk/'+str(diskc)+'/size',c[7]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   status='AVAIL'
   if c[7]=='-':
    status='FAULT'
    cmdline=['/pace/etcdput.py',myhost+'/free/disk/'+str(diskc)+'/status',status]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)

 
