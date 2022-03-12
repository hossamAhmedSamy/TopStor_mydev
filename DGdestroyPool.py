#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
import json
from etcdget import etcdget as get
from etcdput import etcdput as put 
from broadcast import broadcast as broadcast 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost as sendhost
def send(*bargs):
	queuethis('DGdestroyPool.py','running',bargs[-1])
	if(len(bargs) < 3):
		args=bargs[0].split()
	else:
		args=bargs
	pool=args[0]
	x=get('deletedpool','--prefix')
	try:
	 oldx=x[0][1]
	except:
	 oldx='0'
	print('x',oldx)
	pool=str(pool).split()[-1]
	with open('/root/DGdespool2','w') as f:
		f.write(str(bargs))
	put('deletedpool',oldx.replace('/'+str(pool),'')+'/'+str(pool))
	with open('/root/DGdespool','w') as f:
		f.write('deletkey='+str(x)+'/'+str(pool)+'\n')
	with open('/root/DGdespool','a') as f:
		f.write('args='+str(args)+'\n')
	z=[]
	with open('/root/DGdespool','a') as f:
		f.write('pool='+pool+'\n')
	owner=args[-2]
	with open('/root/DGdespool','a') as f:
		f.write('owner='+owner+'\n')
	myhost=hostname()
	with open('/root/DGdespool','a') as f:
		f.write('myhost='+myhost+'\n')
	ownerip=get('leader',owner)
	if ownerip[0]== -1:
		ownerip=get('known',owner)
		if ownerip[0]== -1:
			return 3
	z=['/TopStor/pump.sh','DGdestroyPool']
	for arg in args[:-2]:
		z.append(arg)
	msg={'req': 'DGsetPool', 'reply':z}
	sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
	with open('/root/DGdespool','a') as f:
		f.write('myhost='+ownerip[0][1]+' '+str(msg)+' recvreply '+myhost+'\n')
	with open('/root/DGdespool','a') as f:
		f.write('ClearCache /TopStor/pump.sh ClearCache /TopStordata/'+pool)
	broadcast('ClearCache','/TopStor/pump.sh','ClearCache','/TopStordata/'+pool)
	queuethis('DGdestroyPool.py','stop',bargs[-1])
	return 1

if __name__=='__main__':
 with open('/root/DGdespool3','w') as f:
  f.write(str(sys.argv))
 send(*sys.argv[1:])
