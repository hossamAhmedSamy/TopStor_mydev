#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import heapq



def heapthis(*args):
 logfile = args[0]
 stamps = dict()
 with open(logfile) as f:
  for l in f:
   line = l.split(' ')
   if len(line) < 3:
    continue
   linestamp = int(line[6])
   if linestamp not in stamps:
     stamps[linestamp] = []
   stamps[linestamp].append({ 'task':line[5].split('.py')[0], 'user':line[4], 'status':line[3], \
     'node':line[2], 'at':line[1], 'on':line[0]})
    
 stampseq = list(stamps) 
 heapq.heapify(stampseq)
 otask = dict()
 ctask = dict()
 while stampseq:
  stamp = heapq.heappop(stampseq)
  for st in stamps[stamp]:
   if st['task'] not in otask:
    otask[st['task']] = dict() 
   if st['task'] not in ctask:
    ctask[st['task']] = [] 
   if st['status'] not in 'stop':
    otask[st['task']][st['status']] = {'stamp':stamp, 'node':st['node'],'at':st['at'],'on':st['on']}
   else:
    cutask = otask[st['task']]
    cutask[st['status']] = {'stamp':stamp, 'node':st['node'],'at':st['at'],'on':st['on']}
    ctask[st['task']].append(cutask.items())
    otask[st['task']] = dict() 
 for x in otask:
  if otask[x]:
   print(x,otask[x])
 
 
if __name__=='__main__':
 heapthis(*sys.argv[1:])
