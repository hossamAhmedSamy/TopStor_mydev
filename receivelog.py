#!/bin/python3.6
import subprocess
from ast import literal_eval as mtuple
import socket
from os import listdir
from os.path import isfile, join

myhost=socket.gethostname()
fpath='/var/www/html/des20/Data/'

cmdline=['/pace/etcdget.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(result.stdout).replace('known/','')[2:][:-3].split('\\n')
cmdline=['/pace/etcdget.py','broadcast/response','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
broad=str(result.stdout).replace('broadcast/response/','')[2:][:-3].split('\\n')
######### if no broadcast response from othrs
isbroad=0
if broad==[''] or all(myhost in mtuple(x.replace('\\',''))[0] for x in broad):
 onlyfiles = [f for f in listdir(fpath) if isfile(join(fpath, f)) and "TopStor.log." in f]
 if onlyfiles==[''] or len(known) > len(onlyfiles):
  cmdline=['/pace/etcdput.py','broadcast/request/'+myhost, '1']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  exit()
 mini=99999999999999999
 for f in onlyfiles:
  with open(fpath+f) as ff:
  
   last=int(str(ff.readlines()[-1]).split(' ')[5][1:][:-3])
   if last < mini: 
    mini=last
 cmdline=['/pace/etcdput.py','broadcast/request/'+myhost, str(mini+1)]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 exit()
cmdline=[]
counter=0
for k in broad:
 k=k.replace('\\','')
 k=mtuple(k)
 host=k[0].split('/')[0]
 if host==myhost:
  continue
 cmdline=[]
 counter=0
 with  open('/var/www/html/des20/Data/TopStor.log.'+host,'at') as f:
  a=str(k[1])
  h=mtuple(a)
  for m in h:
   ss=str(m).replace('[','').replace(']','')+'\n'
   cmdline.append(ss)
  f.writelines(cmdline[::-1])
 cmdline=['/pace/etcdput.py','broadcast/confirmed/'+host+'/'+myhost, 'done']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
