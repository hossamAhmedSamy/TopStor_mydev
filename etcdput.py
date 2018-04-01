#!/bin/python3.6
import subprocess,sys
import json

key=sys.argv[1]
val=sys.argv[2]
endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'));
for x in data['members']:
 endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
cmdline=['etcdctl','-w','json','--endpoints='+endpoints,'put',key,val]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
print(result)
