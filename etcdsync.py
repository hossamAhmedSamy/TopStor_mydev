#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple


thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
cmdline=['/pace/etcdget.py',key,'--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
if(result.stdout==b''):
 print('-1')
 exit(1)
mylist=str(result.stdout).replace(key+'/','')[2:][:-3].split('\\n')
for item in mylist:
 x=mtuple(item)
 cmdline=['/pace/etcdputlocal.py',thehost, tokey+'/'+x[0], x[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
