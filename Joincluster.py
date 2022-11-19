#!/usr/bin/python3
import subprocess,sys, datetime,socket
from logqueue import queuethis
import json
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from etcdgetlocalpy import etcdget as get 
import logmsg

myhost = get('clusternode')[0] 
myip = get('clusternodeip')[0] 
leaderip = get('leaderip')[0]
leader = get('leader')[0]
leaderip = get('leaderip')[0]
logmsg.initlog(leaderip, myhost)
def dosync(leader,sync, *args):
  global leaderip
  dels(leaderip, sync)
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

def do(data):
 name=data['name']
 user=data['user']
 queuethis('AddHost','running',user)
 logmsg.sendlog('AddHostst01','info',user,name)
 put(leaderip, 'allowedPartners',name)
 dosync(leader,'Partnr_str_', 'sync/allowedPartners/Add_'+myhost+'_'+myip+'/request','Partnr_str_'+str(stamp())) 
 queuethis('AddHost','stop',user)

if __name__=='__main__':
 do(*sys.argv[1:])
