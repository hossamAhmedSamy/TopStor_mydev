#etcdip=`cat /etc/hosts | grep etcd | awk '{print $1}'`
SLEEP
etcdip='ETCDIP'
etcd --listen-client-urls http://$etcdip:2379 --advertise-client-urls http://$etcdip:2380
