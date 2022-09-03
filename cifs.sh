#!/bin/sh
cd /TopStor
export ETCDCTL_API=3
enpdev='enp0s8'
pool=`echo $@ | awk '{print $1}'`
vol=`echo $@ | awk '{print $2}'`
ipaddr=`echo $@ | awk '{print $3}'`
ipsubnet=`echo $@ | awk '{print $4}'`
vtype=`echo $@ | awk '{print $5}'`
echo $@ > /root/cifsparam
allvols=`./etcdget.py volumes --prefix`
replivols=`echo $allvols | grep $vol `
echo $replivols | grep active 
if [ $? -ne 0 ];
then
 echo it is not active
 exit
fi
leaderall=` ./etcdget.py leader --prefix `
leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
myhost=`hostname`
#docker rm -f `docker ps -a | grep -v Up | grep $ipaddr | awk '{print $1}'` 2>/dev/null
echo cifs $@
ipaddrinfo=`/pace/etcdget.py ipaddr/$myhost $vtype-ipaddr`
rightip=`echo $ipaddrinfo | awk -F"'," '{print $2}' | awk -F"'" '{print $2}' | sed "s/${vol}\///g" | sed "s/\/${vol}//g" | sed "s/${vtype}\-${ipaddr}\///g" | sed "s/${vtype}\-$ipaddr//g"`
otherip=`/pace/etcdget.py ipaddr $vtype-$ipaddr | grep -v $myhost | wc -c`
othervtype=`/pace/etcdget.py ipaddr $ipaddr | grep -v $vtype | wc -c`
/TopStor/logqueue.py `basename "$0"` running $userreq
if [ $otherip -ge 5 ];
then 
 echo another host is holding the ip
 echo otherip=$otherip
 /TopStor/logqueue.py `basename "$0"` stop $userreq
 exit
fi
if [ $othervtype -ge 5 ];
then 
 echo the ip is used by another protocol 
 /TopStor/logqueue.py `basename "$0"` stop $userreq
 exit
fi
#clearvol=`./prot.py clearvol $vol | awk -F'result=' '{print $2}'`
#redvol=`./prot.py redvol $vol | awk -F'result=' '{print $2}'`
resname=$vtype'-'$ipaddr
if [[ $rightip == '' ]];
then
 echo nothing found
 rightip=''
 rightvols=$vol
else
 echo found other vols
 #rightvols=`/pace/etcdget.py ipaddr/$myhost/$ipaddr/$ipsubnet | sed "s/$resname\///g"`'/'$vol
 rightvols=$rightip'/'$vol
fi
 
 echo /pace/etcdput.py ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols
 /pace/etcdput.py ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols
 stamp=`date +%s`;
 /pace/etcdput.py sync/ipaddr/__/request ipaddr_$stamp
 /pace/etcdput.py sync/ipaddr/__/request/$leader ipaddr_$stamp
 #/pace/broadcasttolocal.py ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols 
 /sbin/pcs resource create $resname ocf:heartbeat:IPaddr2 ip=$ipaddr nic=$enpdev cidr_netmask=$ipsubnet op monitor interval=5s on-fail=restart
 /sbin/pcs resource group add ip-all $resname 
 mounts=`echo $rightvols | sed 's/\// /g'`
 echo rightvol=$rightvols
 echo mounts=$mounts
 mount=''
 rm -rf /TopStordata/tempsmb.$ipaddr
 for x in $mounts; 
 do
  replivols=`echo $allvols | grep $x `
  echo $replivols | grep active
  if [ $? -ne 0 ];
  then
   continue
  fi
  mount=$mount' -v /'$pool'/'$x':/'$pool'/'$x':rw '
  cat /TopStordata/smb.$x >> /TopStordata/tempsmb.$ipaddr
 done
 echo mount=$mount
 cp /TopStordata/tempsmb.$ipaddr  /TopStordata/smb.$ipaddr
 cp /TopStor/VolumeCIFSupdate.sh /etc/
 dockers=`docker ps -a`
 echo $dockers | grep $resname
 if [ $? -eq 0 ];
 then
  docker stop $resname 
  docker rm -f $resname
 fi
 docker run -d $mount --privileged \
  -e "HOSTIP=$ipaddr"  \
  -p $ipaddr:135:135 \
  -p $ipaddr:137-138:137-138/udp \
  -p $ipaddr:139:139 \
  -p $ipaddr:445:445 \
  -v /etc/localtime:/etc/localtime:ro \
  -v /TopStordata/smb.${ipaddr}:/config/smb.conf:rw \
  -v /etc/:/hostetc/   \
  -v /var/lib/samba/private:/var/lib/samba/private:rw \
  --name $resname 10.11.11.124:5000/smb
  sleep 3
  docker exec $resname sh /hostetc/VolumeCIFSupdate.sh

/TopStor/logqueue.py `basename "$0"` finish $userreq
