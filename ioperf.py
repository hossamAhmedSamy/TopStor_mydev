#!/bin/python3.6
import subprocess
from time import time
from etcdput import etcdput as put 
from etcddel import etcddel as dels
import socket


myhost=socket.gethostname()
cmdline='iostat -k'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
cpures = result[:4]
diskres = result[6:]
diskresdict = {}
for dsk in diskres:
 dsklst = dsk.split()
 if len(dsklst) < 1 :
  continue
 readpercent = (100*float(dsklst[4]))/(float(dsklst[4])+float(dsklst[5]))
 diskresdict[dsk.split()[0]] = {'tps': dsk.split()[1], 'throuput': round((float(dsk.split()[2])+float(dsk.split()[3]))/2,2), 'read': round(readpercent,2) }
cmdline='lsscsi'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
result = [(x.split()[3],x.split()[5].replace('/dev/','')) for x in result if 'LIO' in x ]
disks = {}
for res in result:
 if res[1] in diskresdict:
  disks[res[1]] = diskresdict[res[1]].copy()
  disks[res[1]]['name'] = res[0]
dels('dskperf',myhost)
for dsk in disks:
 thedsk = disks[dsk]
 put('dskperf/'+myhost+'/'+thedsk['name'], str(thedsk['tps'])+'/'+str(thedsk['throuput'])+'/'+str(thedsk['read'])+'/'+dsk)
with open('/pacedata/perfmon') as f:
 perfmon = f.readline()
if perfmon:
 with open('/Topstordata/dskperfmon.txt','a') as f:
 f.write(str(time())+' dskperf/'+myhost+'/'+thedsk['name']+'\t '+str(thedsk['throuput'])+'/'+str(thedsk['read'])+'/'+dsk)
