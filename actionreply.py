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
 if r["req"]=='user':
  userlist=''
  with open('/etc/passwd') as f:
   userlist=f.read()
  with open('/root/recv','a') as f:
   f.write('userlist:'+str(userlist)+'\n')
  for x in r["reply"]:
   if x[0] not in userlist:
    cmdline=['/TopStor/UnixAddUser_sync',x[0],x[2],x[1]]
    with open('/root/recv','a') as f:
     f.write('adding user '+str(cmdline)+'\n')
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   elif x[2] not in userlist:
    cmdline=['/TopStor/UnixChangePass_sync',x[2],x[0]]
    with open('/root/recv','a') as f:
     f.write('changing password of user '+str(cmdline)+'\n')
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   else:
    with open('/root/recv','a') as f:
     f.write('no user change is found ')
  
# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
