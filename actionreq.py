#!/bin/python3.6
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from sendhost import sendhost as send
def do(body,myhost):
 z=[]
 msg={}
 r=mtuple(body[2:][:-1])
 print(r)
# print("receved from",r["host"],' request for: ',r["req"])
# mylist=get('run',r["req"])
 with open('/root/recv','w') as f:
  f.write('I got a message from '+r["host"]+' : '+r["req"]+'\n')
 if r["req"]=='user':
  with open('/etc/passwd') as f:
   revf=f.readlines()
   for line in revf:
    if 'TopStor' in line:
     l=line.split(':')
     ll=line.split('TopStor')[1].split(':/')[0]
     z.append((l[0],l[2],ll)) 
     with open('/root/recv','a') as f:
      f.write('found user '+l[0]+'\n')
  if r["host"] =='localhost':
   with open('/root/recv','a') as f:
    f.write('request was from localhost\n')
   print(str(z))
  host=get('known/'+r["host"])
  with open('/root/recv','a') as f:
   f.write('sender ip is  : '+str(host[0])+'\n')
  if len(str(host[0])) > 3:
   msg={'req': r["req"], 'reply':z}
   with open('/root/recv','a') as f:
    f.write('preparing \n')
   with open('/root/recv','a') as f:
    f.write('I am ('+myhost+') sending to '+r["host"]+' : \n')
    f.write(str(msg)+'\n')
   send(host[0], str(msg), 'recvreply', str(myhost))
  else:
   with open('/root/recv','a') as f:
    f.write('it is not known sender... ignoring \n')
    exit()
 print(z)  
# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"',sys.argv[2]) 
 exit()
