#!/bin/python3.6
import subprocess,sys
import json

thehost=sys.argv[1]
key=sys.argv[2]
try:
 prefix=sys.argv[3]
except:
 prefix=''
endpoints=''
#data=json.load(open('/pacedata/runningetcdnodes.txt'));
#for x in data['members']:
# endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
endpoints='http://'+thehost+':2378'
cmdline=['etcdctl','--endpoints='+endpoints,'get',key,prefix]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
if(result.stdout==b''):
  print('-1')
  exit(1)
try:
 if(prefix !=''):
  mylist=str(result.stdout)[2:][:-3].split('\\n')
  zipped=zip(mylist[0::2],mylist[1::2])
  for x in zipped:
   print(x)
 else:
  if(result==['']):
   print('-1')
  print(str(result.stdout).split(key)[1][2:][:-3])
 
except:
 print('-1')
