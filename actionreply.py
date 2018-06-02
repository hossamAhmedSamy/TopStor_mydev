#!/bin/python3.6
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
  cmdline='/TopStor/logmsg.sh Unlin1005 info system'
  cmdline=cmdline.split()
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
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
  cmdline='/TopStor/logmsg.sh Unlin1006 info system'
  cmdline=cmdline.split()
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)


if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
