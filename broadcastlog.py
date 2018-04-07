#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
cmdline=['/pace/etcdget.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(result.stdout).replace('known/','')[2:][:-3].split('\\n')
if known==['']:
 print('no partners')
 exit();
cmdline=['/pace/etcdget.py','broadcast/confirmed','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
conf=str(result.stdout).replace('broadcast/confirmed/','')[2:][:-3].split('\\n')
if conf != ['']:
 cmdline=['/pace/etcddel.py','broadcast','--prefix']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 exit()
  
cmdline=['/pace/etcdget.py','broadcast/request','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
br=str(result.stdout).replace('broadcast/request/','')[2:][:-3].split('\\n')
if br==['']:
 print('no request')
 exit();
broad=[]
for c in br:
 if myhost in mtuple(c)[0]:
  continue
 broad.append(mtuple(c))
start=min(broad,key=lambda t: t[1])
broad=[]
counter=0
with open('/var/www/html/des20/Data/TopStor.log','rt') as f:
 for line in f:
  line=str(line).split(' ')
  if float(start[1]) <= float(line[5]):
   counter+=1
   line[5]=line[5].replace('\n','')
   cmdline=['/pace/etcdput.py','broadcast/response/'+myhost+'/'+str(counter),str(line)]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   print(line)

