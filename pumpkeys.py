#!/usr/bin/python3
import sys, subprocess
from etcdgetlocalpy import etcdget as get 
from sendhost import sendhost
myhost = get('clusternode')[0] 
myip = get('clusternodeip')[0]
clusterip = get('leaderip')[0]
with open('/root/tmptmp','w') as f:
 f.write(str(clusterip))
def pumpkeys(*bargs):
 print(str(bargs))
 partnerip = bargs[0]
 replitype = bargs[1]
 repliport = bargs[2]
 phrase = bargs[3]
 cmdline = '/TopStor/preparekeys.sh '+partnerip
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0].replace(' ','_spc_')
 z=['/TopStor/pump.sh','receivekeys.sh',myhost,myip,clusterip, replitype, repliport, phrase, result]
 msg={'req': 'Exchange', 'reply':z}
 print(msg)
 sendhost(partnerip, str(msg),'recvreply',myhost)
 

if __name__=='__main__':
 pumpkeys(*sys.argv[1:])
