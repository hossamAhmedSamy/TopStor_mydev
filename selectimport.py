#!/bin/python3.6
from etcdgetpy import etcdget as get
from logqueue import queuethis
from etcdput import etcdput as put 
from etcddel import etcddel as deli 
import poolall 
import socket, sys, datetime, subprocess
from broadcast import broadcast as broadcast 
from sendhost import sendhost
from time import time as timestamp

from ast import literal_eval as mtuple
#from zpooltoimport import zpooltoimport as importables

def selecthost(minhost,hostname,hostpools):
	if len(hostpools) < minhost[1]:
		minhost = (hostname, len(hostpools))
	return minhost

def electimport(myhost, allpools, leader, *arg):
	knowns=get('known','--prefix')
	for poolpair in allpools:
		if myhost not in poolpair[0]:
			continue
		pool=poolpair[0].split('/')[1]
		chost=poolpair[1]
		nhost=str(get('poolsnxt/'+pool)[0])
		if nhost in str(knowns) and chost not in nhost:
			print('continue')
			continue
		stamp=int(datetime.datetime.now().timestamp())	
		if nhost != '-1':
			deli('poolsnxt',nhost)
			put('sync/poolsnxt/Del_poolsnxt_'+nhost+'/request','poolsnxt_'+str(stamp))
			put('sync/poolsnxt/Del_poolsnxt_'+nhost+'/request/'+leader,'poolsnxt_'+str(stamp))
		hosts=get('hosts','/current')
		if len(hosts) < 2:
			continue   # just to clean the poolsnxt or otherwise it would be 'return'
		minhost = ('',float('inf'))
		for host in hosts: 
			hostname = host[0].split('/')[1]
			if hostname == chost:
				continue
			hostpools=mtuple(host[1])
			minhost = selecthost(minhost,hostname,hostpools)
			print('minhost',minhost)
		put('poolsnxt/'+pool,minhost[0])
		put('sync/poolsnxt/Add_'+pool+'_'+minhost[0]+'/request','poolsnxt_'+str(stamp))
		put('sync/poolsnxt/Add_'+pool+'_'+minhost[0]+'/request/'+leader,'poolsnxt_'+str(stamp))
	return

 
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
		timestamp=int(datetime.datetime.now().timestamp())-5
		locked=get('lockedpools','--prefix')
		ownerstatus=get('cannotimport/'+owner)
		if hostpair[0] in ownerstatus:
			continue
		#if hostpair[0] in importedpools:
		#	continue
		if hostpair[0] in locked:
			print('in locked')
			lockinfo=get('lockedpools/'+hostpair[0])
			oldtimestamp=lockinfo[0].split('/')[1]
			lockhost=lockinfo[0].split('/')[0]
			lockhostip=get('leader/'+lockhost)
			if( '-1' in str(lockhostip)):
				lockhostip=get('known/'+lochost)
				if('-1' in str(lockhostip)):
					deli('lockedpools/'+pool)
					continue
			if int(timestamp) > int(oldtimestamp):
				put('lockedpools/'+pool,lockhost+'/'+str(timestamp))
				z=['/TopStor/pump.sh','ReleasePoolLock',pool]
				msg={'req': 'ReleasePoolLock', 'reply':z}
				sendhost(lockhostip[0], str(msg),'recvreply',myhost)

			continue
		#importedpools.append(hostpair[0])
		ownerip=get('leader',owner)
		if ownerip[0]== -1:
			ownerip=get('known',owner)
			if str(ownerip[0])== '-1':
				return
		put('lockedpools/'+hostpair[0],owner+'/'+str(timestamp))
#################### end of election
		z=['/TopStor/pump.sh','Zpool','import','-c','/TopStordata/'+hostpair[0],'-am']

		msg={'req': 'Zpoolimport', 'reply':z}
		sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		#z=['/TopStor/pump.sh','ClearCache',hostpair[0][1:]]
		#msg={'req': 'ClearCache', 'reply':z}
		#sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
		deli('toimport',hostpair[0])
	return

if __name__=='__main__':
	myhost=socket.gethostname()
	leader=get('leader','--prefix')[0][0].replace('leader/','')
	allpools=get('pools/','--prefix')
	electimport(myhost,allpools,leader, *sys.argv[1:])
	cmdline='cat /pacedata/perfmon'
	
	perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)

	#if '1' in perfmon:
	#	queuethis('selectimport.py','start','system')
	#importpls(myhost,allinfo,*sys.argv[1:])
	#if '1' in perfmon:
	#	queuethis('selectimport.py','stop','system')
