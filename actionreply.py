#!/bin/python3.6
import codecs, logmsg
from ast import literal_eval as mtuple
from etcdget import etcdget as get
import subprocess
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
  with open('/root/recv','a') as f:
   f.write('preparing cifs:'+str(r["reply"][0])+'\n')
  cifsconf=codecs.decode(r["reply"][0],'hex')
  cifsconf=cifsconf.decode('utf-8')
  with open('/root/recv','a') as f:
   f.write('cifs conf: '+cifsconf+'\n')
  with open('/etc/samba/smb.conf','w') as f:
   f.write(cifsconf)
########## if logall ######################
 elif r["req"]=='logall':
  with open('/root/recv','a') as f:
   f.write('preparing logs:\n')
  conf=codecs.decode(r["reply"][0],'hex')
  conf=conf.decode('utf-8')
  with open('/root/recv','a') as f:
   f.write('logs: '+conf+'\n')
  with open('/var/www/html/des20/Data/TopStorglobal.log','w') as f:
   f.write(conf)
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
 


if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
