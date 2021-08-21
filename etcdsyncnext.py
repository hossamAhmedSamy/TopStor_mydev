#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from logqueue import queuethis


with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
if '1' in perfmon:
 queuethis('syncnext','start_still','system')
thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
result=get(key,'--prefix')
print("the result",result)
if result==[]:
 print('-1')
 if '1' in perfmon:
  queuethis('syncnext','stop_cancelled','system')
 exit(1)
for item in result:
 x=item[0].replace('/','')
 x=x.replace(str(key),'')
 if x =='':
   adding='';
 else:
   adding='/'+x
 print('mez',thehost,tokey+adding,item[1])
 cmdline=['/pace/etcdputlocal.py',thehost, tokey+adding, item[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
if '1' in perfmon:
 queuethis('syncnext','stop','system')
