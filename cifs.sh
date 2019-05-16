#!/bin/sh
cd /TopStor
export ETCDCTL_API=3
enpdev='enp0s8'
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
ipaddr=`echo $@ | awk '{print $3}'`
ipsubnet=`echo $@ | awk '{print $4}'`
echo $@ > /root/cifsparam
clearvol=`./prot.py clearvol $volname | awk -F'result=' '{print $2}'`
if [ $clearvol != '-1' ];
then
 docker stop $clearvol 
 docker container rm $clearvol 
 /sbin/pcs resource delete --force $clearvol  2>/dev/null
fi
redvol=`./prot.py redvol $volname | awk -F'result=' '{print $2}'`
if [ $redvol != '-1' ];
then
 redipaddr=`echo $redvol | awk -F'-' '{print $NF}'`
 /TopStor/delblock.py start${vol}_only stop${vol}_only /TopStordata/smb.${redipaddr}  ;
 cp /TopStordata/smb.${redipaddr}.new /TopStordata/smb.${redipaddr};
 docker exec -it $redvol smbcontrol smbd reload-config
fi
rightvol=`/pace/etcdget.py ipaddr/$ipaddr`
if [ $rightvol -eq '-1' ];
then
 resname=cifs-$pool-$ipaddr
 /pace/etcdput.py ipaddr/$ipaddr $resname/$vol
 /pace/broadcasttolocal.py ipaddr/$ipaddr $resname/$vol 
 docker stop $resname 
 docker container rm $resname 
 /sbin/pcs resource delete --force $resname  2>/dev/null
 /sbin/pcs resource create $resname ocf:heartbeat:IPaddr2 ip=$ipaddr nic=$enpdev cidr_netmask=$ipsubnet op monitor interval=5s on-fail=restart
 /sbin/pcs resource group add ip-all $resname 
 yes | cp /etc/{passwd,group,shadow} /opt/passwds
 cp /TopStor/smb.conf /TopStordata/smb.$ipaddr
 cat /TopStordata/smb.${vol}>> /TopStordata/smb.$ipaddr
 docker run -d -v /$pool/$vol:/$pool/$vol:rw --privileged \
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
  --name $resname 10.11.11.124:5000/smb
else
 resname=`echo $rightvol | awk -F'/' '{print $1}'`
 newright=${rightvol}'/'$vol 
 mounts=`echo $newright |sed 's/\// /g'| awk '{$1=""; print}'`
 mount=''
 for x in $mounts; 
 do
  mount=$mount'-v /'$pool'/'$x':/'$pool'/'$x':rw '
 done
 /pace/etcdput.py ipaddr/$ipaddr $newright 
 /pace/broadcasttolocal.py ipaddr/$ipaddr $newright
 cat /TopStordata/smb.${vol} >> /TopStordata/smb.$ipaddr
 docker stop $resname
 docker rm $resname
 docker run -d $mount --privileged \
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
  --name $resname 10.11.11.124:5000/smb
fi

