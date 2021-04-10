#!/bin/python3.6
import sys 
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
stamps = dict()
stampseq = []
otask = dict()
ctask = dict()
lenctask = 0
def heapthis(line):
 global stamps,lenctask, stampseq, otask, ctask
 try:
  linestamp = int(line[-1])
 except:
  with open('/root/logqueueheapexception','a') as f:
   f.write(str(line))
  return 
 if line[2] not in otask:
  otask[line[2]] = dict() 
 if line[2] not in ctask:
  ctask[line[2]] = dict() 
 if linestamp not in stamps:
  stamps[linestamp] = dict()
 stamps[linestamp][line[2]] = []
 st = { 'task':line[3].split('.py')[0], 'user':line[5], 'status':line[4], \
  'at':line[1], 'on':line[0].replace('/',':')}
 stamps[linestamp][line[2]].append(st)
 if st['task'] not in otask[line[2]]:
  otask[line[2]][st['task']] = dict() 
 if st['task'] not in ctask[line[2]]:
  ctask[line[2]][st['task']] = [] 
 if 'stop' not in st['status']:
  otask[line[2]][st['task']][st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
  put('OpenTasks/'+line[2]+'/'+st['task']+'/'+st['status'], str(linestamp)+'/'+st['at']+'/'+st['on'])
 else:
  cutask = otask[line[2]][st['task']]
  if not cutask:
   otask[line[2]][st['task']] = dict() 
  else:
   cutask[st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
   ctask[line[2]][st['task']].append(cutask)
   otask[line[2]][st['task']] = dict() 
   dels('OpenTasks/'+line[2],st['task'])
   lenctask += len(ctask[line[2]][st['task']])
   if lenctask > 20: 
    with open('/TopStordata/taskperf','a') as f:
     f.write(str(ctask)+'\n')
    ctask = dict()
    lenctask = 0
# dels('OpenTasks','--prefix')
# for host in otask:
#  for task in otask[host]:
#   for status in otask[host][task]:
#    if status:
#     put('OpenTasks/'+host+'/'+task+'/'+status, str(otask[host][task][status]['stamp'])+'/'+otask[host][task][status]['at']+'/'+otask[host][task][status]['on'])
 return  
 
 
if __name__=='__main__':
 #heapthis(*sys.argv[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:31', 'dhcp6517', 'selectspare.py', 'start', 'system', '1617989669']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:32', 'dhcp6517', 'addknown.py', 'running', 'system', '1617989671']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:34', 'dhcp6517', 'selectspare.py', 'stop', 'system', '1617989671']
 heapthis(x[1:])
