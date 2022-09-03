#!/bin/python3.6
import subprocess,sys, datetime
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 

def crontoetc(*bargs):
 cmdline='/bin/crontab -l'
 cronsall=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode().split('\n')
 cronsini=[x.replace(' ','%') for x in cronsall if 'hosttrend' in str(x) and len(x) > 2]
 crons=[('Snapperiod/'+x.split('%')[-2]+'/'+x.split('nowhost')[1].split('%')[1]+'/'+x.split('nowhost')[1].split('%')[-1],x) for x in cronsini ]
 cronsini=[x.replace(' ','%') for x in cronsall if 'hosttrend' not in str(x) and len(x) > 2 ]
 crons= crons +  [('Snapperiod/'+x.split('ly.')[0].split('%')[-1]+'ly'+'/'+x.split('nowhost')[1].split('%')[1]+'/'+x.split('nowhost')[1].split('%')[-1],x) for x in cronsini ]
 dels('Snapperiod','--prefix')
 for x in crons:
  put(x[0],x[1])

if __name__=='__main__':
 crontoetc(*sys.argv[1:])
