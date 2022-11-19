#!/usr/bin/python3
import sys, subprocess, os
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from sendhost import sendhost
stamps = dict()
stampseq = []
otask = dict()
ctask = ''
lenctask = 0
def heapthis(leaderip, myhost, line):
 global stamps,lenctask, stampseq, otask, ctask
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
  put(leaderip, 'OpenTasks/'+line[2]+'/'+st['task']+'/'+st['status'], str(linestamp)+'/'+st['at']+'/'+st['on'])
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
   dels(leaderip,'OpenTasks/'+line[2],st['task'])
   lenctask += 1 
   if lenctask > 20: 
    with open('/TopStordata/taskperf','a') as f:
     f.write(ctask)
    thenextlead =get(leaderip, 'nextlead/er')[0]
    if 'dhcp' in str(thenextlead):
     nextlead = thenextlead[0].split('/')[1]
     z = [ctask]
     msg={'req': 'taskperf', 'reply':z}
     sendhost(nextlead, str(msg),'recvreply',myhost)
    cmdline=['/sbin/logrotate','logqueue.cfg','-fv']
    subprocess.run(cmdline,stdout=subprocess.PIPE)
    cmdline=['/bin/touch','/TopStordata/taskperf']
    subprocess.run(cmdline,stdout=subprocess.PIPE)
    ctask = ''
    lenctask = 0
 return  

def syncnextlead(leaderip, myhost, lastfile,archive):
 thenextlead =get(leaderip, 'nextlead/er')[0]
 if 'dhcp' not in str(thenextlead):
  return
 filelist = os.listdir('/TopStordata/')
 filelist = [ x for x in filelist if 'taskperf' in x ]
 filelist.sort()
 filetosend = [ x for x in filelist if filelist.index(x) > filelist.index(lastfile) ]
 nextlead = thenextlead[0].split('/')[1]
 if int(archive) or len(filetosend):
  filetosend.append('taskperf')
 for filethis in filetosend:
  z=['/TopStordata/'+filethis]
  with open(z[0],'r') as f:
   z.append(f.read())
   #print(z)
   msg={'req': 'syncthisfile', 'reply':z}
   sendhost(nextlead, str(msg),'recvreply',myhost)
 with open('/root/syncnextleadtmp','w') as f:
   f.write('sent to '+nextlead+' '+str(filetosend)+' archive '+str(archive)+'\n')
 return  
 
if __name__=='__main__':
 #heapthis(*sys.argv[1:])
 syncnextlead('taskperf-2021041522',1)
 
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:31', 'dhcp6517', 'testlogqueue2.py', 'start', 'system', '1617989669']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:32', 'dhcp6517', 'test2loguque2.py', 'running', 'system', '1617989671']
 heapthis(x[1:])
 x=['/TopStor/logqueue2.sh', '04/09/2021', '20:34:34', 'dhcp6517', 'test3logqueue2.py', 'stop', 'system', '1617989671']
 heapthis(x[1:])
