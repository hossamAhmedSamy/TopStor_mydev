#!/bin/python3.6
from ast import literal_eval as mtuple
from etcdget import etcdget as get
def do(body):
 z=[]
 with open('/root/recv','a') as f:
  f.write('Recevied a reply:'+str(body))
 exit()
 r=mtuple((body[2:][:-1]))
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
 print(z)  
# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
