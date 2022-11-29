#!/bin/sh
cd /TopStor
export ETCDCTL_API=3
enpdev='enp0s8'
leaderip=`echo $@ | awk '{print $1}'`
pool=`echo $@ | awk '{print $2}'`
vol=`echo $@ | awk '{print $3}'`
ipaddr=`echo $@ | awk '{print $4}'`
ipsubnet=`echo $@ | awk '{print $5}'`
vtype=`echo $@ | awk '{print $6}'`
echo $@ > /root/cifsparam
	myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
	myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
	leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
	echo $leader | grep $myhost
	if [ $? -ne 0 ];
	then
 		etcd=$myhostip
	else
 		etcd=$leaderip
 	fi
echo '#################################################################################################33'
echo etcd=$etcd
echo '#################################################################################################33'
allvols=`/pace/etcdget.py $etcd volumes --prefix`
replivols=`echo $allvols | grep $vol `
echo $replivols | grep active 
if [ $? -ne 0 ];
then
 echo it is not active
 exit
fi
#docker rm -f `docker ps -a | grep -v Up | grep $ipaddr | awk '{print $1}'` 2>/dev/null
ipaddrinfo=`/pace/etcdget.py $etcd ipaddr/$myhost $vtype-ipaddr`
rightip=`echo $ipaddrinfo | awk -F"'," '{print $2}' | awk -F"'" '{print $2}' | sed "s/${vol}\///g" | sed "s/\/${vol}//g" | sed "s/${vtype}\-${ipaddr}\///g" | sed "s/${vtype}\-$ipaddr//g"`
otherip=`/pace/etcdget.py $etcd ipaddr $vtype-$ipaddr | grep -v $myhost | wc -c`
othervtype=`/pace/etcdget.py $etcd ipaddr $ipaddr | grep -v $vtype | wc -c`
 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` running $userreq
if [ $otherip -ge 5 ];
then 
 echo another host is holding the ip
 echo otherip=$otherip
 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` stop $userreq
 exit
fi
if [ $othervtype -ge 5 ];
then 
 echo the ip is used by another protocol 
 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` stop $userreq
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
 #rightvols=`/pace/etcdgetlocal.py ipaddr/$myhost/$ipaddr/$ipsubnet | sed "s/$resname\///g"`'/'$vol
 rightvols=$rightip'/'$vol
fi
 
 echo /pace/etcdput.py $leaderip ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols
 /pace/etcdput.py $leaderip ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols
 stamp=`date +%s`;
 /pace/etcdput.py $leaderip sync/ipaddr/__/request ipaddr_$stamp
 /pace/etcdput.py $leaderip sync/ipaddr/__/request/$leader ipaddr_$stamp
 #/pace/broadcasttolocal.py ipaddr/$myhost/$ipaddr/$ipsubnet $resname/$rightvols 
 mounts=`echo $rightvols | sed 's/\// /g'`
 echo rightvol=$righ$etcd tvols
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
 nmcli conn mod cmynode +ipv4.addresses ${ipaddr}/$ipsubnet
 nmcli conn up cmynode
 docker run -d $mount --privileged \
  -e "HOSTIP=$ipaddr"  \
  -p $ipaddr:135:135 \
  -p $ipaddr:137:137/udp \
  -p $ipaddr:138:138/udp \
  -p $ipaddr:139:139 \
  -p $ipaddr:445:445 \
  -v /TopStordata/smb.${ipaddr}:/config/smb.conf:rw \
  -v /TopStordata/smb.${ipaddr}:/etc/samba/smb.conf:rw \
  -v /etc/:/hostetc/   \
  -v /var/lib/samba/private:/var/lib/samba/private:rw \
  --name $resname moataznegm/quickstor:smb
  sleep 3
  docker exec $resname sh /hostetc/VolumeCIFSupdate.sh

 docker exec etcdclient /TopStor/logqueue.py `basename "$0"` finish $userreq
