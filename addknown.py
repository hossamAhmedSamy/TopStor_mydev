#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple
import json
endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'))
for x in data['members']:
 endpoints+=str(x['clientURLs'])[2:][:-2]
cmdline=['./etcdget.py','possible','--prefix']
possibleres=subprocess.run(cmdline,stdout=subprocess.PIPE)
possible=str(possibleres.stdout)[2:][:-3].split('\\n')
print('the possible',possible)
for x in possible:
 print('x=',mtuple(x)[0], mtuple(x)[1])
 cmdline=['etcdctl','--endpoints='+endpoints,'del',mtuple(x)[0]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print('result=',result)
 cmdline=['etcdctl','--endpoints='+endpoints,'put','known'+mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result)
