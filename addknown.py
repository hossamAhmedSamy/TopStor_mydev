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
try:
 for x in possible:
  print('x=',mtuple(x)[0], mtuple(x)[1])
  cmdline=['etcdctl','--endpoints='+endpoints,'del',mtuple(x)[0]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  print('result=',result)
  cmdline=['etcdctl','--endpoints='+endpoints,'put','known/'+mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['./etcdput.py','change/'+mtuple(x)[0]+'/booted',mtuple(x)[1]]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['./iscsiwatchdog.sh','2>/dev/null']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  print(result)
except:
 print('possible is empty')
cmdline=['./etcdget.py','known','--prefix']
knownres=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(knownres.stdout)[2:][:-3].replace('known/','').split('\\n')
for kno in known:
 kn=mtuple(kno) 
 cmdline=['./etcdgetlocal.py',str(kn[1]),'local','--prefix','2>/dev/null']
 heartres=subprocess.run(cmdline,stdout=subprocess.PIPE)
 heart=str(heartres.stdout)[2:][:-3].split('\\n')
 if(heart == ['-1']):
  cmdline=['/pace/hostlost.sh',str(kn[0])]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/etcddel.py','known/'+str(kn[0])]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
 elif (mtuple(heart[0])[1] not in str(kn[1])):
  cmdline=['/pace/hostlost.sh',str(kn[0])]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/etcddel.py','known/'+str(kn[0])]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
   
 
