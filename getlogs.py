#!/bin/python3.6
from logqueue import queuethis
import subprocess
from time import time
import sys

with open('/var/www/html/des20/msgsglobal.txt') as f:
 logcatalog = f.read().split('\n')
logdict = dict()
for log in logcatalog:
 msgcode= log.split(':')[0]
 logdict[msgcode] = log.replace(msgcode+':','').split(' ')

def onedaylog():
 severity = ('info','warning','error')
 unsuclogon = 'Lognfa0'
 onedaylog = {'failedlogon': []} 
 for sev in severity:
  onedaylog[sev] = []
  nowis = int(time())
  nowfixed = str(nowis)[:4]
  cmdline='./grepthis.sh '+nowfixed+' '+sev+' /var/www/html/des20/Data/TopStorglobal.log'
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
  for res in result:
   if len(res.split()) < 4:
    continue
   if int(res.split()[-1]) > (nowis-(60*60*24*7)):
    onedaylog[sev].append(res)
    if 'Lognfa0' in res:
     onedaylog['failedlogon'].append(res)
 return onedaylog

def notifthis(notifbody,loc=3):
 msg = logdict[notifbody[loc]]
 msgbody = '.'
 notifc = 6
 for word in msg[4:]:
  if word == ':':
   msgbody = msgbody[:-1]+' '+notifbody[notifc]+'.'
   notifc += 1
  elif len(word) > 0:
   msgbody = msgbody[:-1]+' '+word+'.' 
 notif = { 'importance':msg[0].replace(':',''), 'msgcode': notifbody[3], 'date':notifbody[0], 'time':notifbody[1],
	 'host':notifbody[2], 'type':notifbody[4], 'user': notifbody[5], 'msgbody': msgbody[1:]} 
 return notif


def getlogs(lines=100, *args):
 notiflist = []
 cmd = 'tail -n '+str(lines)+' /var/www/html/des20/Data/TopStorglobal.log'
 result=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE)
 result = str(result.stdout.decode('utf8')).split('\n')
 for line in result:
   notifbody = line.replace('@@@',' ').replace('@@','').replace('@',' ').split(' ')
   if len(notifbody) < 6:
    continue
   notifbody[3],notifbody[4],notifbody[5] = notifbody[5],notifbody[3],notifbody[4]
   notiflist.append(notifthis(notifbody=notifbody))
 print(notiflist)
 return notiflist  

 
if __name__=='__main__':
 getlogs(*sys.argv[1:])
