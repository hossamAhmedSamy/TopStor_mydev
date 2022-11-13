#!/usr/bin/python3
import os, time
from etcdget import etcdget as get
stamps = dict()
stampseq = []
otask = dict()
oseq = []
ctask = dict()
def heapthis(queue,stage):
 global stamps, stampseq, otask, ctask
 with open(queue,'r') as f:
  while stage: 
   if stage == 1:
    stage = 0
   print('read line')
   for l in f:
    line = l.split(' ')
    try:
     linestamp = int(line[6])
    except:
     print('problem')
     print(line)
     continue
    if line[2] not in otask:
     otask[line[2]] = dict() 
    if line[2] not in ctask:
     ctask[line[2]] = dict() 
    if linestamp not in stamps:
     stamps[linestamp] = dict()
     stamps[linestamp][line[2]] = []
    st = { 'task':line[5].split('.py')[0], 'user':line[4], 'status':line[3], \
     'at':line[1], 'on':line[0]}
    stamps[linestamp][line[2]].append(st)
    if st['task'] not in otask[line[2]]:
     otask[line[2]][st['task']] = dict() 
    if st['task'] not in ctask[line[2]]:
     ctask[line[2]][st['task']] = [] 
    if st['status'] not in 'stop':
     otask[line[2]][st['task']][st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
      
    else:
     cutask = otask[line[2]][st['task']]
     if not cutask:
      otask[line[2]][st['task']] = dict() 
      continue
     cutask[st['status']] = {'stamp':linestamp,'at':st['at'],'on':st['on']}
     ctask[line[2]][st['task']].append(cutask)
     otask[line[2]][st['task']] = dict() 
   time.sleep(0.07)
   os.system('clear')
   oseq = []
   o = 0
   for host in otask:
    for task in otask[host]:
     for status in otask[host][task]:
      if status:
       oseq.append((host,task,status,otask[host][task][status]['stamp']))
       o +=1
   oseq.sort(key= lambda x:x[-1])
   for x in oseq:
    print(x)
   c = 0
   for host in ctask:
    for task in  ctask[host]:
     for _ in ctask[host][task]:
      c +=1
   print('o=',o , 'c=',c) 
 
 
if __name__=='__main__':
 logqueue = '/var/www/html/des20/Data/TopStorqueue.log'
 fifoqueue = '/tmp2/msgqueue'
 #heapthis(logqueue,1)
 heapthis(fifoqueue,2)
