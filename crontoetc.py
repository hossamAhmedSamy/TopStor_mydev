#!/bin/python3.6
import subprocess,sys, datetime
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 

def crontoetc(*bargs):
 cmdline='/bin/crontab -l'
 crons=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 crons=str(crons).split('\\n')
 crons=[x.replace(' ','%') for x in crons if 'host' in str(x)]
 crons=[('Snapperiod/'+x.split('nowhost')[1].split('%')[1]+'/'+x.split('nowhost')[1].split('%')[-1],x) for x in crons ]
 dels('Snapperiod','--prefix')
 for x in crons:
  put(x[0],x[1])

if __name__=='__main__':
 crontoetc(*sys.argv[1:])
