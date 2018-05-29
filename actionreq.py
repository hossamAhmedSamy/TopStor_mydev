#!/bin/python3.6
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from sendhost import sendhost as send
def do(body,myhost):
 z=[]
 r=mtuple(body[2:][:-1])
 print(r)
# print("receved from",r["host"],' request for: ',r["req"])
# mylist=get('run',r["req"])
 with open('/root/recv','w') as f:
  f.write('I got a message from '+r["host"]+' : '+r["req"])
 if r["req"]=='user':
  with open('/etc/passwd') as f:
   revf=f.readlines()
   for line in revf:
    if 'TopStor' in line:
     l=line.split(':')
     ll=line.split('TopStor')[1].split(':/')[0]
     z.append((l[0],l[2],ll)) 
  if r["host"] =='localhost':
   print(str(z))
  host=get('known/'+r["host"])
  with open('/root/recv','a') as f:
   f.write('sender ip is  : '+str(host[0]))
  if len(host) > 3:
   msg=str({'host': myhost, 'req': str(z)})
   with open('/root/recv','a') as f:
    f.write('I am ('+myhost+') sending to'+r["host"]+' : ')
    f.write(msg)
  send(myhost, msg, 'recvreply', myhost)
 print(z)  
# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"',sys.argv[2]) 
 exit()
 z=[]
 mylist=get('run',sys.argv[1])
 if sys.argv[1]=='user':
  with open('/etc/passwd') as f:
   revf=f.readlines()
   for line in revf:
    if 'TopStor' in line:
     l=line.split(':')
     ll=line.split('TopStor')[1].split(':/')[0]
     z.append((l[0],l[2],ll)) 
 print(z)  
