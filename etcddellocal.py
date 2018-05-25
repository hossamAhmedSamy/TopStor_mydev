#!/bin/python3.6
import subprocess,sys
import json

if sys.argv[-1]=='--prefix':
 pointer=-1
else:
 pointer=0
endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'));
endpoints='http://'+sys.argv[1]+':2378'
if len(sys.argv) > 2:
 cmdline=['etcdctl','--endpoints='+endpoints,'get',sys.argv[2],'--prefix']
else:
 cmdline=['etcdctl','--endpoints='+endpoints,'get',sys.argv[2]]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
mylist=str(result.stdout)[2:][:-3].split('\\n')
zipped=zip(mylist[0::2],mylist[1::2])
if mylist==['']:
 print('-1')
 exit()
if len(sys.argv) > 3 and sys.argv[3] !='--prefix':
 todel=[]
 args=sys.argv[3:]
 for x in args:
  for y in zipped:
   if x in str(y):
    todel.append(y[0])
else:
 todel=mylist
if todel == []:
 print('-1')
 exit()
count=0
for key in todel:
 cmdline=['etcdctl','--endpoints='+endpoints,'del',key]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 reslist=str(result.stdout)[2:][:-3]
 if '1' in reslist:
  count+=1
print(count)
