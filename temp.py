#!/usr/bin/python3
from etcdgetpy import etcdget as get
with open('/TopStor/msgsglobal.txt') as f:
 logcatalog = f.read().split('\n')
logdict = dict()
for log in logcatalog:
 msgcode= log.split(':')[0]
 logdict[msgcode] = log.replace(msgcode+':','').split(' ')
allinfo = 0


leaderip = '10.11.11.250'
myhost = get(leaderip, 'clusternode')[0]

notifbody = get(leaderip, 'notification')[0].split(' ')[1:]
requests = get(leaderip, 'request','--prefix')
requestdict = {}
for req in requests:
 reqname = req[0].split('/')[1]
 reqhost = req[0].split('/')[2]
 reqstatus = req[1]
 if reqname not in requestdict:
  requestdict[reqname] = {}
 requestdict[reqname][reqhost] = reqstatus
msg = logdict[notifbody[3]]
msgbody = '.'
notifc = 6
for word in msg[4:]:
 if word == ':':
  try:
   msgbody = msgbody[:-1]+' '+notifbody[notifc]+'.'
  except:
   msgbody = msgbody +' '+notifbody+'parseerror.'
   print('notification parse error')
   print('############################')
  notifc += 1
 elif len(word) > 0:
  msgbody = msgbody[:-1]+' '+word+'.' 
notif = { 'importance':msg[0].replace(':',''), 'msgcode': notifbody[3], 'date':notifbody[0], 'time':notifbody[1],
 'host':notifbody[2], 'type':notifbody[4], 'user': notifbody[5], 'msgbody': msgbody[1:],'requests':requestdict, 'response':'Ok'}
 
print('notif',notif)
