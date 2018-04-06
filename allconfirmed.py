#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
import socket

myhost=socket.gethostname()
cmdline=['/pace/etcdget.py','change','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
change=str(result.stdout)[2:][:-3].split('\\n')
if len(change) < 2:
 print('no change')
 exit()
cmdline=['/pace/etcdget.py','conf','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
confirmed=str(result.stdout)[2:][:-3].split('\\n')
if len(confirmed) < 2:
 print('no confirm')
 exit()
cmdline=['/pace/etcdget.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(result.stdout)[2:][:-3].split('\\n')
if len(known) < 2:
 print('no partners')
 exit()

print('mylist=',mylist)
for x in mylist:
 y=mtuple(x)
 z=y[0].replace('change/','')
 if 'disk' not in z :
  with open('/pacedata/'+z,'w') as f:
   f.write(y[1])
 cmdline=['/pace/etcdput.py','confirmed/'+myhost+'/'+z, y[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
