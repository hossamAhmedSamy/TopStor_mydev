#!/usr/bin/python3
import pika, sys, subprocess
import actionreply


def callback(ch, method, properties, body):
 actionreply.do(myip, str(body))


cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
#myip=sys.argv[1]
cred = pika.PlainCredentials('rabb_Mezo', 'YousefNadody')
param = pika.ConnectionParameters(myip,5672, '/', cred)
conn = pika.BlockingConnection(param)
chann= conn.channel()
chann.queue_declare(queue='recvreply')
#chann.basic_consume(callback, queue='recvreply', no_ack=True)
chann.basic_consume('recvreply',callback, True)
chann.start_consuming()
