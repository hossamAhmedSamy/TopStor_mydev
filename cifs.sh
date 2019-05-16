#!/bin/sh
export ETCDCTL_API=3
enpdev='enp0s8'
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
ipaddr=`echo $@ | awk '{print $3}'`
ipsubnet=`echo $@ | awk '{print $4}'`
echo $@ > /root/cifsparam
rightvol=`/pace/etcdget.py ipaddr/$ipaddr`
if [ $rightvol -eq '-1' ];
then
 /pace/etcdput.py ipaddr/$ipaddr 1/$vol
 /pace/broadcasttolocal.py ipaddr/$ipaddr 1/$vol 
 docker stop cifs-$pool-$vol
 docker container rm cifs-$pool-$vol
 /sbin/pcs resource delete --force ip-$pool-$vol  2>/dev/null
 /sbin/pcs resource create ip-$pool-$vol ocf:heartbeat:IPaddr2 ip=$ipaddr nic=$enpdev cidr_netmask=$ipsubnet op monitor interval=5s on-fail=restart
 /sbin/pcs resource group add ip-all ip-$pool-$vol
 yes | cp /etc/{passwd,group,shadow} /opt/passwds
 cp /TopStor/smb.conf /TopStordata/smb.$ipaddr
 cat /TopStordata/smb.${vol}>> /TopStordata/smb.$ipaddr
 docker run -d -v /$pool:/$pool:rw --privileged \
  -e "HOSTIP=$ipaddr"  \
  -p $ipaddr:135:135 \
  -p $ipaddr:137-138:137-138/udp \
  -p $ipaddr:139:139 \
  -p $ipaddr:445:445 \
  -v /etc/localtime:/etc/localtime:ro \
  -v /TopStordata/smb.${ipaddr}:/config/smb.conf:rw \
  -v /opt/passwds/passwd:/etc/passwd:rw \
  -v /opt/passwds/group:/etc/group:rw \
  -v /opt/passwds/shadow:/etc/shadow:rw \
  -v /var/lib/samba/private:/var/lib/samba/private:rw \
  --name cifs-$pool-$vol 10.11.11.124:5000/smb
else
 count=`echo $rightvol | awk -F'/' '{print $1}'`
 origvol=`echo $rightvol | awk -F'/' '{print $2}'`
 newcount=$((count+1))
 /pace/etcdput.py ipaddr/$ipaddr $newcount/$origvol
 /pace/broadcasttolocal.py ipaddr/$ipaddr $newcount/$origvol 
 cat /TopStordata/smb.${vol} >> /TopStordata/smb.$ipaddr
 docker exec -it cifs-$pool-$origvol smbcontrol reload-config
fi

