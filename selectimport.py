#!/bin/python3.6
from etcdget import etcdget as get
from etcddel import etcddel as deli 
import socket, sys, subprocess
from sendhost import sendhost
from ast import literal_eval as mtuple
#from zpooltoimport import zpooltoimport as importables

def importpls(myhost,allinfo,*args):
	if(len(allinfo) < 0):
		return
	pools={}
	for host in allinfo:
		if 'nothing' in host[1]:
			continue
		for pool in mtuple(host[1]):
			pools[pool[0]]=[]
	for host in allinfo:
		if 'nothing' in host[1]:
			continue
		for pool in mtuple(host[1]):
			pools[pool[0]].append((host[0].split('/')[1],pool[1],pool[2]))
	hosts=[]
	importedpools=['hi']
	for pool in pools.keys():
		hosts.append((pool,max(pools[pool],key=lambda x:x[1])[0])) 
	for hostpair in hosts:
		if hostpair[0] == 'nothing':
			continue
		owner=hostpair[1]
################# elect the host to import the pool ###############
                locked=get('lockedpools','--prefix')
		ownerstatus=get('cannotimport/'+owner)
		if hostpair[0] in ownerstatus:
			continue
		if hostpair[0] in importedpools:
			continue
		if hostpair[0] in locked:
			continue
		importedpools.append(hostpair[0])
		ownerip=get('leader',owner)
		if ownerip[0]== -1:
			ownerip=get('known',owner)
			if ownerip[0]== -1:
				return 3
		put('lockedpools/'+hostpair[0],'1')
#################### end of election
		z=['/TopStor/pump.sh','Zpool','import','-c','/TopStordata/'+hostpair[0],'-am']

		msg={'req': 'Zpoolimport', 'reply':z}
		sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		#z=['/TopStor/pump.sh','ClearCache',hostpair[0][1:]]
		#msg={'req': 'ClearCache', 'reply':z}
		#sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		deli('to','--prefix')
	return

if __name__=='__main__':
 myhost=socket.gethostname()
 x=subprocess.check_output(['pgrep','selectimport'])
 x=str(x).replace("b'","").replace("'","").split('\\n')
 x=[y for y in x if y != '']
 if(len(x) > 1 ):
  print('process still running',len(x))
  exit()
 allinfo=get('to','--prefix')
 importpls(myhost,allinfo,*sys.argv[1:])
 
 
