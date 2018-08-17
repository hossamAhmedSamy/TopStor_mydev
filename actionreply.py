#!/bin/python3.6
import codecs, logmsg
import binascii
from ast import literal_eval as mtuple
from etcdget import etcdget as get
import subprocess
import logmsg
def do(body):
 z=[]
 with open('/root/recv','w') as f:
  f.write('Recevied a reply:'+body[2:][:-1]+'\n')
 t=mtuple(body[2:][:-1].replace("\\'","'"))
 r=mtuple(t["req"])
 with open('/root/recv','a') as f:
   f.write('Request details:'+r['req']+'\n')
########## if user ######################
 if r["req"]=='user':
  logmsg.sendlog('Unlin1005', 'info', 'system')
  with open('/etc/passwd') as f:
   revf=f.readlines()
   for line in revf:
    if 'TopStor' in line:
     l=line.split(':')
     with open('/root/recv','a') as f:
      f.write('syncing user: '+l[0]+'\n')
     cmdline=['/TopStor/UnixDelUser_sync',l[0], 'system']
     result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  with open('/root/recv','a') as f:
   f.write('Syncing users:\n')
  for x in r["reply"]:
   cmdline=['/TopStor/UnixAddUser_sync',x[0],x[2],x[1]]
   with open('/root/recv','a') as f:
    f.write('adding user '+str(cmdline)+'\n')
   cmdline=['/TopStor/UnixAddUser_sync',x[0],x[2],x[1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('Unlin1006', 'info', 'system')
########## if cifs ######################
 elif r["req"]=='cifs':
  logmsg.sendlog('Actst1000', 'info', 'system')
  with open('/root/recv','a') as f:
   f.write('preparing cifs:'+str(r["reply"][0])+'\n')
  cifsconf=codecs.decode(r["reply"][0],'hex')
  cifsconf=cifsconf.decode('utf-8')
  with open('/root/recv','a') as f:
   f.write('cifs conf: '+cifsconf+'\n')
  with open('/etc/samba/smb.conf','w') as f:
   f.write(cifsconf)
  logmsg.sendlog('Actsu1000', 'info', 'system')
########## if logall ######################
 elif r["req"]=='logall':
  logmsg.sendlog('Actst1001', 'info', 'system')
  with open('/root/recv','a') as f:
   f.write('preparing logs:\n')
  conf=codecs.decode(r["reply"][0],'hex')
  conf=conf.decode('utf-8')
  with open('/root/recv','a') as f:
   f.write('logs: '+conf+'\n')
  with open('/var/www/html/des20/Data/TopStorglobal.log','w') as f:
   f.write(conf)
  logmsg.sendlog('Actsu1001', 'info', 'system')
########## if msg ###############
 elif r["req"]=='msg':  
  with open('/root/recv','a') as f:
   f.write('received msg from parnter :'+str(r["reply"])+'\n')
   f.write('type of message :'+str(type(r["reply"]))+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if msg2 ###############
 elif r["req"]=='msg2':  
  with open('/root/recv','a') as f:
   f.write('received msg2 from parnter :'+str(r["reply"])+'\n')
   f.write('type of message :'+str(type(r["reply"]))+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if DGsetPool ###############
 elif r["req"]=='DGsetPool':  
  with open('/root/recv','a') as f:
   f.write('received DGsetPool from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if VolumeCreate ###############
 elif r["req"]=='VolumeCreate':  
  with open('/root/recv','a') as f:
   f.write('received VolumeCreate from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if VolumeDelete ##############
 elif r["req"]=='VolumeDelete':  
  with open('/root/recv','a') as f:
   f.write('received VolumeCreate from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if Zpool (direct command..etc) ##############
 elif r["req"]=='Zpool':  
  with open('/root/recv','a') as f:
   f.write('received Zpool from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if Zpoolimport (import) ##############
 elif r["req"]=='Zpoolimport':  
  pool=r["reply"][4].split('/')[2]
  logmsg.sendlog('Zpst02','info','system',pool)
  with open('/root/recv','a') as f:
   f.write('received Zpool from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
  logmsg.sendlog('Zpsu02','info','system',pool)
########## if clear cache ##############
 elif r["req"]=='ClearCache':  
  with open('/root/recv','a') as f:
   f.write('received ClearCache from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if broadcast ##############
 elif r["req"]=='broadcast':  
  with open('/root/recv','a') as f:
   f.write('received broadcast from parnter :'+str(r["reply"])+'\n')
  result=subprocess.run(r["reply"],stdout=subprocess.PIPE)
########## if Movecache ##############
 elif r["req"]=='Movecache':  
  with open('/root/recv','a') as f:
   f.write('received cachemove from partner :'+'\n')
  cachename=r["reply"][0]
  cachefile=r["reply"][1]
  with open(cachename,'wb') as f:
   f.write(cachefile)
 


if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
