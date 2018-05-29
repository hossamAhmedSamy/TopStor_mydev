#!/bin/python3.6
from ast import literal_eval as mtuple
from etcdget import etcdget as get
def do(body):
 z=[]
 with open('/root/recv','a') as f:
  f.write('Recevied a reply:'+str(body))
 r=mtuple((body[2:][:-1]))
# print("receved from",r["host"],' request for: ',r["req"])
# mylist=get('run',r["req"])
 if r["req"]=='user':
  with open('/root/recv','a') as f:
   f.write('User list in reply:'+str(r["reply"]))
 print(z)  
# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"') 
 exit()
