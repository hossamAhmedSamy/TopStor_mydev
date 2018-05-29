#!/bin/python3.6
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from sendhost import sendhost as send
def do(body):
 z=[]
 r=mtuple((body[2:][:-1]), myhost)
# print("receved from",r["host"],' request for: ',r["req"])
# mylist=get('run',r["req"])
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
      return(str(z)) 
     host=get('known/'+r["host"])
     if len(host) > 3:
      msg=str({'host': myhost, 'req': str(z)})
      send(myhost, msg, 'recvreply', myhost)
      return(str(z)) 
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
