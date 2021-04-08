#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import heapq
stamps = dict()
stampseq = []
heapq.heapify(stampseq)
otask = dict()
ctask = dict()
def heapthis(queue,stage):
 global stamps, stampseq, otask, ctask
 with open(queue,'r') as f:
  while stage: 
   if stage == 1:
    stage = 0
   for l in f:
    line = l.split(' ')
    if len(line) < 3:
     continue
    linestamp = int(line[6])
    heapq.heappush(stampseq,linestamp) 
    if linestamp not in stamps:
     stamps[linestamp] = []
    st = { 'task':line[5].split('.py')[0], 'user':line[4], 'status':line[3], \
    'node':line[2], 'at':line[1], 'on':line[0]}
    stamps[linestamp].append(st)
    if st['task'] not in otask:
     otask[st['task']] = dict() 
    if st['task'] not in ctask:
     ctask[st['task']] = [] 
    if st['status'] not in 'stop':
     otask[st['task']][st['status']] = {'stamp':linestamp, 'node':st['node'],'at':st['at'],'on':st['on']}
    else:
     cutask = otask[st['task']]
     cutask[st['status']] = {'stamp':linestamp, 'node':st['node'],'at':st['at'],'on':st['on']}
     ctask[st['task']].append(cutask)
     otask[st['task']] = dict() 
   o = 0
   for x in otask:
    if otask[x]:
     o +=1
   c = 0
   for x in ctask:
    for _ in  ctask[x]:
     c +=1
   print('o=',o , 'c=',c) 
 
 
if __name__=='__main__':
 logqueue = '/var/www/html/des20/Data/TopStorqueue.log'
 fifoqueue = '/tmp2/msgqueue'
 heapthis(logqueue,1)
 heapthis(fifoqueue,2)
