#!/bin/python3.6
import codecs
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from sendhost import sendhost as send
def do(body,myhost):
 z=[]
 msg={}
 r=mtuple(body[2:][:-1])
 print(r)
# print("receved from",r["host"],' request for: ',r["req"])
# mylist=get('run',r["req"])
 with open('/root/recv','w') as f:
  f.write('I got a message from '+r["host"]+' : '+r["req"]+'\n')
 host=get('known/'+r["host"])
 with open('/root/recv','a') as f:
  f.write('sender ip is  : '+str(host[0])+'\n')
 if len(str(host[0])) < 4:
  with open('/root/recv','a') as f:
   f.write('it is not known sender... ignoring \n')
   r["req"]='uknown_host:'+r["host"]
############## received "user" request #################
 if r["req"]=='user':
  with open('/etc/passwd') as f:
   revf=f.readlines()
   for line in revf:
    if 'TopStor' in line:
     l=line.split(':')
     ll=line.split('TopStor')[1].split(':/')[0]
     z.append((l[0],l[2],ll)) 
     with open('/root/recv','a') as f:
      f.write('found user '+l[0]+'\n')
  if r["host"] =='localhost':
   with open('/root/recv','a') as f:
    f.write('request was from localhost\n')
   print(str(z))
  else:
   msg={'req': r["req"], 'reply':z}
   with open('/root/recv','a') as f:
    f.write('preparing \n')
   with open('/root/recv','a') as f:
    f.write('I am ('+myhost+') sending to '+r["host"]+' : \n')
    f.write(str(msg)+'\n')
   send(host[0], str(msg), 'recvreply', str(myhost))
############# CIFS data #####################
 elif r["req"]=='cifs':
  with open('/root/recv','a') as f:
   f.write('preparing cifs data \n')
  with open('/etc/samba/smb.conf') as f:
   cifsconf=f.read()
  cifsconf=cifsconf.encode()
  bcifs=codecs.encode(cifsconf,'hex')
  z.append(bcifs)
  msg={'req': r["req"], 'reply':z}
  send(host[0],str(msg), 'recvreply',str(myhost))
############# logall data #####################
 elif r["req"]=='logall':
  with open('/root/recv','a') as f:
   f.write('preparing logfile \n')
  with open('/var/www/html/des20/Data/TopStorglobal.log') as f:
   conf=f.read()
  conf=conf.encode()
  bconf=codecs.encode(conf,'hex')
  z.append(bconf)
  msg={'req': r["req"], 'reply':z}
  send(host[0],str(msg), 'recvreply',str(myhost))
############## uknown request ###############
 else:
  with open('/root/recv','a') as f:
   f.write('uknown request:  \n')
   f.write(r["req"]+' \n')
  


# if r["req"]=='user':
if __name__=='__main__':
 import sys
 msg=str({'host': 'localhost', 'req': sys.argv[1]})
 do('b"'+msg+'"',sys.argv[2]) 
 exit()
