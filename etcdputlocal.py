#!/bin/python3.6
import subprocess,sys
import json

myip=sys.argv[1]
key=sys.argv[2]
val=sys.argv[3]
endpoints=''
#data=json.load(open('/pacedata/runningetcdnodes.txt'));
#for x in data['members']:
# endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
endpoints='http://'+myip+':2378'
cmdline=['etcdctl','-w','json','--endpoints='+endpoints,'put',key,val]
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
print(result)
