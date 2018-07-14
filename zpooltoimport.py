#!/bin/python3.6
import subprocess, socket
from etcdput import etcdput as put

def zpooltoimport(*args):
 myhost=socket.gethostname()
 cmdline='/sbin/zpool import'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 y=str(result)[2:][:-3].replace('\\t','').split('\\n')
 #with open("tmp") as f:
 # y=f.read()
 #y=y.split('\n')
 #with open("zfslist.txt") as f:
 # zfslist=f.read()
 #zfslist2=zfslist.split('\n')
 cmdline='/bin/lsscsi -is'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 lsscsi=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 freepool=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 raidtypes=['mirror','raidz','stripe']
 raid2=['log','cache','spare']
 zpool=[]
 stripecount=0
 spaces=-2
 raidlist=[]
 disklist=[]
 for a in y:
  b=a.split()
  if "pdhc" in a and  'pool' not in a:
   raidlist=[]
   volumelist=[]
   zdict={}
   zdict={ 'name':b[0], 'status':b[1],  'raidlist': raidlist ,'volumes':volumelist}
   zpool.append(zdict)
  elif any(raid in a for raid in raidtypes):
   spaces=len(a.split(a.split()[0])[0])
   disklist=[]
   zdict={ 'name':b[0], 'status':b[1],'disklist':disklist }
   raidlist.append(zdict)
  elif any(raid in a for raid in raid2):
   spaces=len(a.split(a.split()[0])[0])
   disklist=[]
   zdict={ 'name':b[0], 'status':'NA','disklist':disklist }
   raidlist.append(zdict)
  elif 'scsi' in a:
    diskid='-1'
    host='-1'
    size='-1' 
    if  len(a.split('scsi')[0]) < (spaces+2) or (len(raidlist) < 1 and len(zpool)> 0):
     disklist=[]
     zdict={ 'name':'stripe-'+str(stripecount), 'status':'NA','disklist':disklist }
     raidlist.append(zdict)
     stripecount+=1
    for lss in lsscsi:
     z=lss.split()
     if z[6] in b[0]:
      diskid=lsscsi.index(lss)
      host=z[3].split('-')[1]
      size=z[7]
      break
    zdict={'name':b[0], 'status':b[1],'id': str(diskid), 'host':host, 'size':size}
    disklist.append(zdict)
  else:
    zdict={'name':'na','status':a}
 put('toimport/'+myhost,str(zpool))
 #put('hosts/dhcp31481/current',str(zpool))
 return zpool 
if __name__=='__main__':
 zpooltoimport(*sys.argv[1:])
