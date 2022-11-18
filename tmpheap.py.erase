#!/usr/bin/python3
import sys 
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from socket import gethostname as hostname
from sendhost import sendhost
stamps = dict()
stampseq = []
otask = dict()
ctask = ''
lenctask = 0
def heapthis(line):
 global stamps,lenctask, stampseq, otask, ctask
 myhost=hostname()
 try:
  linestamp = int(line[-1])
 except:
  with open('/root/logqueueheapexception','a') as f:
   f.write(str(line))
  return 
 if line[2] not in otask:
  otask[line[2]] = dict() 
 #if line[2] not in ctask:
 # ctask[line[2]] = dict() 
 if linestamp not in stamps:
  stamps[linestamp] = dict()
 stamps[linestamp][line[2]] = []
 st = { 'task':line[3].split('.py')[0], 'user':line[5], 'status':line[4], \
  'at':line[1], 'on':line[0].replace('/',':')}
 stamps[linestamp][line[2]].append(st)
 if st['task'] not in otask[line[2]]:
  otask[line[2]][st['task']] = dict() 
 #if st['task'] not in ctask[line[2]]:
 # ctask[line[2]][st['task']] = [] 
 if 'stop' not in st['status']:
  otask[line[2]][st['task']][st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
  put('OpenTasks/'+line[2]+'/'+st['task']+'/'+st['status'], str(linestamp)+'/'+st['at']+'/'+st['on'])
 else:
  cutask = otask[line[2]][st['task']].copy()
  if not cutask:
   otask[line[2]][st['task']] = dict() 
  else:
   cutask[st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
   for stall in cutask:
    ctask +=line[2]+' '+st['task']+' '+stall+' '+str(cutask[stall]['stamp'])+' '+cutask[stall]['at']+' '+cutask[stall]['on']+'\n'
   #ctask[line[2]][st['task']].append(cutask)
   otask[line[2]][st['task']] = dict() 
   dels('OpenTasks/'+line[2],st['task'])
   lenctask += 1 
   if lenctask > 0: 
    with open('/TopStordata/taskperftmp','a') as f:
     f.write(ctask)
    
    nextlead = get('nextlead/er')[0].split('/')[1]
    z = [ctask]
    msg={'req': 'taskperf', 'reply':z}
    sendhost(nextlead, str(msg),'recvreply',myhost)
    ctask = ''
    lenctask = 0
 return  
 
 
if __name__=='__main__':
 #heapthis(*sys.argv[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:31', 'dhcp6517', 'selectspare.py', 'start', 'system', '1617989669']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:32', 'dhcp6517', 'addknown.py', 'running', 'system', '1617989671']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:34', 'dhcp6517', 'selectspare.py', 'stop', 'system', '1617989671']
 heapthis(x[1:])
