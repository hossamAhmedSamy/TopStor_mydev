#!/usr/bin/python3
import subprocess,sys, datetime
from time import time
from logqueue import queuethis
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from deltolocal import deltolocal
from broadcasttolocal import broadcasttolocal as broadcasttolocal 
from Evacuatelocal import setall
from etcdget import etcdget as get 
import logmsg
def do(leaderip,myhost, *args):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis(leaderip, 'Evacuate','toremove',args[-1])
 logmsg.sendlog(leaderip, 'Evacuaest01','info',args[-1],args[-2])
 evacip = get(leaderip , 'ActivePartners/'+args[-2])[0]
 leader=get(leaderip, 'leader','--prefix')[0][0].replace('leader/','')
 stamp = time()
 put(leaderip, 'sync/evacuatehost/syncfn_setall_'+args[-2]+'_'+evacip+'_'+args[-1]+'/request', 'evacuatehost_'+str(stamp))
 put(leaderip, 'sync/evacuatehost/syncfn_setall_'+args[-2]+'_'+evacip+'_'+args[-1]+'/request/'+myhost, 'evacuatehost_'+str(stamp))
 if myhost == leader:
  setall(args[-2],evacip,args[-1])

if __name__=='__main__':
 do(*sys.argv[1:])
