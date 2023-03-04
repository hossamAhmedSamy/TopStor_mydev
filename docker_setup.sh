myclusterf='/topstorwebetc/mycluster'
mynodef='/topstorwebetc/mynode'
myhost=`hostname`
echo '# init' > /etc/exports
rm -rf /TopStordata/exportip.*
echo ${myhost}$@ | grep reboot
if [ $? -ne 0 ];
then
 nmcli conn up mynode
 zpool export -a
fi
targetcli clearconfig confirm=True	
echo ${myhost}$@ | egrep 'init|local'
if [ $? -eq 0 ];
then
	myhost='dhcp'`echo $RANDOM$RANDOM | cut -c -6`
	hostname $myhost
	echo $myhost > /etc/hostname
	echo frstreboot > /root/hostname
	echo InitiatorName=iqn.1994-05.com.redhat:$myhost > /etc/iscsi/initiatorname.iscsi
	reboot
fi
cat /root/hostname | grep frstreboot
if [ $? -eq 0 ];
then
	echo $myhost > /root/hostname
	reboot
fi
eth1='enp0s8'
eth2='enp0s8'
echo $1 | grep restart
if [ $? -eq 0 ];
then
	/TopStor/resetdocker.sh
fi
if [ $# -ge 1 ];
then 
	echo $1 | egrep 'stop|reboot|reset'
	if [ $? -eq 0 ];
	then
		/TopStor/resetdocker.sh
		echo $1 | grep reset
		if [ $? -eq 0 ];
		then
			rm -rf /root/node*
			rm  -rf /root/etcddata/* 
			echo yes | cp /TopStor/passwd /etc/
			echo yes | cp /TopStor/group /etc/
			echo reset > /root/nodestatus
			systemctl start target
			targetcli clearconfig confirm=True	
			targetcli saveconfig 
			/TopStor/resetdocker.sh	
			nmcli conn up clusterstub 
			nmcli conn delete mynode 
			nmcli conn delete mycluster 
			hostname localhost
			echo localhost > /etc/hostname
		fi
		echo $1 | egrep 'reboot|reset'
		if [ $? -eq 0 ];
		then
			reboot
		fi
		echo $1 | grep 'stop'
		if [ $? -eq 0 ];
		then
			echo hihihihihi
			exit
		fi
	fi
	echo $1 | grep restart 
	if [ $? -ne 0 ];
	then
		eth1=$1
	fi
fi
if [ $# -ge 2 ];
then
	eth2=$1
fi

mynodedev=$eth1
myclusterdev=$eth1
data1dev=$eth2
data2dev=$eth2
setenforce 0
aliast='alias'
targetcli clearconfig confirm=true
#nmcli conn delete clusterstub 
#nmcli conn delete mynode 
#nmcli conn delete mycluster 
nmcli conn up clusterstub
nmcli conn up mynode
nmcli conn delete cmynode
nmcli conn delete cmycluster
isinitn=`cat /root/nodeconfigured`'s'
echo $isinitn | grep 'yess'
if [ $? -ne 0 ];
then
	#mynode='10.11.11.244/24'
	isconf='no'
	x=$(( ( RANDOM % 40 )  + 3 ))
	mynode='10.11.11.'$x'/24'
	nmcli conn add con-name mynode type ethernet ifname $mynodedev ip4 $mynode
	nmcli conn delete clusterstub
	nmcli conn add con-name clusterstub type ethernet ifname $myclusterdev ip4 169.168.12.12 
	#nmcli conn up clusterstub 

	ping -w 3 10.11.11.250
	if [ $? -ne 0 ];
	then
		mycluster='10.11.11.250/24'
		isconf_prim='noyes'
		isprimary=1
		echo the ping didn\'t find the initial cluster 250 so I am primary
	else
		mycluster=$mynode
		isconf_prim='nono'
		isprimary=0
		echo the ping found the initial cluster so I will not be primary
	fi
	nmcli conn add con-name mycluster type ethernet ifname $myclusterdev ip4 $mycluster
else
	isconf='yes'
	mynode=`nmcli conn show mynode | grep ipv4.addresses | awk '{print $2}'`
	mycluster=`nmcli conn show mycluster | grep ipv4.addresses | awk '{print $2}'`
	myclusterip=`echo $mycluster | awk -F'/' '{print $1}'`
	ping -w 3 $myclusterip 
	if [ $? -ne 0 ];
	then 
		isconf_prim='yesyes'
		isprimary=1
	else
		isconf_prim='yesno'
		isprimary=0
	fi
fi
myclusterip=`echo $mycluster | awk -F'/' '{print $1}'`
mynodeip=`echo $mynode | awk -F'/' '{print $1}'`
myip=$mynodeip
echo $mynodedev | grep $myclusterdev
if [ $? -eq 0 ];
then
	case $isconf_prim in 
		nono)
		;;
		noyes)
		;;
		yesno)
		;;
		yesyes)
		;;
	esac
	if [ $isprimary -ne 0 ];
	then
		echo I am prmary
		echo nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode ip4 $mycluster
		nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode ip4 $mycluster
	else
		echo I am a cluster node 
		nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode
	fi
else
	case $isconf_prim in 
		nono)
		;;
		noyes)
		;;
		yesno)
		;;
		yesyes)
		;;
	esac
	nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode
	nmcli conn add con-name cmycluster type ethernet ifname $myclusterdev ip4 $mycluster
	if [ $isprimary -ne 0 ];
	then
		nmcli conn up cmycluster
	fi

fi
echo adding cmynode
nmcli conn up cmynode
if [[ $isconf == 'yes' ]];
then
	echo strting target
	systemctl start target
	echo starting iscsid
	systemctl start iscsid 
fi
echo starting docker
systemctl start docker

echo starting intdns
docker run --rm --name intdns --hostname intdns --net bridge0 -e DNS_DOMAIN=qs.dom -e DNS_IP=10.11.12.7 -e LOG_QUERIES=true -itd --ip 10.11.12.7 -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/dnshosts:/etc/hosts moataznegm/quickstor:dns
leaderip=$myclusterip
if [ $isprimary -eq 1 ];
then
	utcd=$myclusterip
	leader=$myhost
else
	etcd=$mynodeip
fi

echo nameserver 10.11.12.7 >  /root/gitrepo/resolv.conf
echo starting etcd 
docker run -itd --rm --name etcd --hostname etcd -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $etcd:2379:2379 -v /TopStor/:/TopStor -v /root/etcddata:/default.etcd --net bridge0 moataznegm/quickstor:etcd

echo starting etcdclient 
docker run -itd --rm --name etcdclient --hostname etcdclient -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:etcdclient 
if [[ $isconf_prim == 'nono' ]];
then
 /pace/watchdoginit & disown
 /pace/keepsendingprim & disown
 exit
fi
if [[ $isconf_prim == 'noyes' ]];
then
 /pace/watchdogprim & disown
 /pace/watchdoginit & disown
 /pace/keepsendingprim & disown
fi

echo starting intstub 
docker run -itd --rm --privileged \
  -v /TopStor/smb.conf:/etc/samba/smb.conf:rw \
  -v /etc/:/hostetc/   \
  -v /root/gitrepo/resolv.conf:/etc/resolv.conf \
  -v /var/lib/samba/private:/var/lib/samba/private:rw \
  -v /TopStor/smbuser.sh:/root/smbuser.sh \
  --net bridge0 \
  --name intsmb --hostname intsmb moataznegm/quickstor:smb
 docker exec intsmb sh /hostetc/VolumeCIFSupdate.sh
#docker run -d --rm --name rmq --hostname rmq  -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -p $etcd:5672:5672 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:rabbitmq 
echo starting rabbitmq 
systemctl start rabbitmq-server
rabbitmqctl add_user rabb_Mezo YousefNadody 2>/dev/null
rabbitmqctl set_permissions -p / rabb_Mezo ".*" ".*" ".*" 2>/dev/null
started=0
while [ $started -eq 0 ];
do
		echo waiting etcd to settle 
		docker logs etcd | grep 'successfully notified init daemon' 
		if [ $? -eq 0 ];
	 	then
			started=1
	 	else
		 	sleep 1
	 	fi
done
echo starting > /root/dockerlogs.txt
checkcluster='0'
echo hihi$checkcluster | grep $myclusterip
while [ $? -ne 0 ];
do
	sleep 1
	docker exec etcdclient /pace/etcdputlocal.py clusternodeip $mynodeip
	docker exec etcdclient /pace/etcdputlocal.py clusternode $myhost
	if [ $isprimary -eq 1 ];
	then
		echo initializing etcd params 
		echo docker exec etcdclient /pace/etcdput.py $myclusterip clusternode $myhost
		echo isprimary $isprimary >> /root/dockerlogs.txt
		docker exec etcdclient /TopStor/etcdput.py $myclusterip ActivePartners/$myhost $mynodeip 
		docker exec etcdclient /TopStor/etcdput.py $myclusterip leaderip $myclusterip 
		echo docker exec  etcdclient /TopStor/etcdput.py $myclusterip leaderip $myclusterip >> /root/dockerlogs.txt
		docker exec etcdclient /TopStor/etcdput.py $myclusterip leader $myhost 
		docker exec etcdclient /TopStor/etcdput.py $myclusterip nextlead/er 'None' 
		etcdip=$myculsterip

	else
		echo waiting for me to join the cluster 
		echo isprimaryin0 $isprimary >> /root/dockerlogs.txt
		docker exec etcdclient /pace/etcdget.py $myclusterip Active --prefix | grep $myhost
		if [ $? -ne 0 ];
		then
			docker exec etcdclient /TopStor/etcdput.py $myclusterip possible$myhost $mynodeip 
			echo I joined the cluster
		fi
		stillpossible=1
		while [ $stillpossible -eq 1 ];
		do
			docker exec etcdclient /TopStor/etcdget possible --prefix | grep $myhost
			if [ $? -ne 0 ];
			then
				stillpossible=0
			else
				sleep 2
				echo waiting for me to join the cluster 
			fi
		done
		etcdip=$mynodeip
		stamp=`date +%s%N`
	fi
	echo initializaing volume pool leader clsuternode data
	myalias=`docker exec etcdclient /pace/etcdgetlocal.py $aliast/$myhost`
	leader=`/pace/etcdget.py $myclusterip leader`
	docker exec etcdclient /pace/etcdputlocal.py leader $leader 
	docker exec etcdclient /pace/etcdputlocal.py leaderip $myclusterip
	docker exec etcdclient /pace/etcdputlocal.py clusternode $myhost
	docker exec etcdclient /pace/etcddellocal.py sync/Snapperiod/initial $myhost request/$myhost 2>/dev/null
        docker exec etcdclient /pace/etcddellocal.py pool --prefix 2>/dev/null
	docker exec etcdclient /pace/etcddellocal.py volume --prefix 2>/dev/null
	docker exec etcdclient /pace/etcddellocal.py sync/pool Add_ 2>/dev/null
	docker exec etcdclient /pace/etcddellocal.py sync/pool Del_ 2>/dev/null
	docker exec etcdclient /pace/etcddellocal.py sync/volume Add_ 2>/dev/null
	docker exec etcdclient /pace/etcddellocal.py sync/volume Del_ 2>/dev/null
        docker exec etcdclient /pace/etcdput.py $myclusterip $aliast/$myhost $myalias
	#/TopStor/syncq.py $myclusterip $myhost 2>/root/syncqerror
	stamp=`date +%s%N`
	myalias=`echo $myalias | sed 's/\_/\:\:\:/g'`
	/pace/etcddel.py $myclusterip sync/$aliast/Add_${myhost} --prefix
	if [ $isprimary -ne 0 ];
	then
 		/pace/etcddel.py $myclusterip ready --prefix
 		/pace/etcddel.py $myclusterip sync/ready/Add --prefix
	else
 		/pace/etcddel.py $mynodeip ready --prefix
	
	fi		
	/pace/etcdput.py $myclusterip sync/$aliast/Add_${myhost}_$myalias/request ${aliast}_$stamp.
	/pace/etcdput.py $myclusterip sync/$aliast/Add_${myhost}_$myalias/request/$myhost ${aliast}_$stamp.
	/pace/etcdput.py $myclusterip sync/$aliast/Add_${myhost}_$myalias/request/$leader ${aliast}_$stamp.
	issync=`/pace/etcdget.py $myclusterip sync initial`initial
	echo $issync | grep $myhost
	if [ $? -eq 0 ];
	then
		echo syncrequests only
		echo row 262 checksync init >> /root/checksync
    		docker exec etcdclient /pace/checksyncs.py syncrequest $myclusterip $myhost $myip
       	else
		echo have to syncall
		echo row 266 checksync init >> /root/checksync
		docker exec etcdclient /pace/checksyncs.py syncall $myclusterip $myhost $myip
	fi
	checkcluster=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
	echo $checkcluster >> /root/dockerlogs.txt
	echo hihi$checkcluster | grep $myclusterip
done
#############################3
docker exec etcdclient /TopStor/etcddel.py $etcd pools --prefix 
docker exec etcdclient /TopStor/etcdput.py $etcd mynodeip $mynodeip 
docker exec etcdclient /TopStor/etcdput.py $etcd mynode $myhost 
docker exec etcdclient /TopStor/etcdput.py $etcd leaderip $myclusterip 
docker exec etcdclient /TopStor/etcdput.py $etcd isprimary $isprimary 
isreset=`cat /root/nodestatus`
echo ${isreset}$isprimary | grep reset1
if [ $? -eq 0 ];
then
	echo initializing admin user
	docker exec etcdclient /TopStor/UnixsetUser.py $myclusterip `hostname` admin tmatem
	/TopStor/UnixAddGroup $etcd Everyone usersNoUser admin
	echo runningnode > /root/nodestatus
fi
#rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
if [ $isprimary -eq 1 ];
then
	echo adding all sync inits as I am primary
	echo docker exec etcdclient /pace/checksyncs.py syncinit $etcd
	echo row 293 checksync init >> /root/checksync
	docker exec etcdclient /pace/checksyncs.py syncinit $etcd 
fi
 echo running rabbit receive daemon
 /TopStor/topstorrecvreply.py $etcd & disown
docker exec -it etcdclient /TopStor/etcdput.py $etcd ready/$myhost $mynodeip 



#docker run --restart unless-stopped --name git -v /root/gitrepo:/usr/local/apache2/htdocs/ --hostname sgit -p 10.11.11.252:80:80 -v /root/gitrepo/httpd.conf:/usr/local/apache2/conf/httpd.conf -itd -v /root/gitrepo/resolv.conf:/etc/resolv.conf moataznegm/quickstor:git
templhttp='/TopStor/httpd_template.conf'
rm -rf /TopStordata/httpd.conf
cp /TopStor/httpd.conf /TopStordata/
shttpdf='/TopStordata/httpd.conf'
docker rm -f httpd
docker rm -f flask
rm -rf $httpdf
if [ $isprimary -ne 0 ];
then
	cp $templhttp $shttpdf
	sed -i "s/MYCLUSTERH/$myclusterip/g" $shttpdf
	sed -i "s/MYCLUSTER/$myclusterip/g" $shttpdf
	echo running httpd fowrarder as I am not primary
	docker run --rm --name httpd --hostname shttpd --net bridge0 -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $myclusterip:19999:19999 -p $myclusterip:80:80 -p $myclusterip:443:443 -v $shttpdf:/usr/local/apache2/conf/httpd.conf -v /root/topstorwebetc:/usr/local/apache2/topstorwebetc -v /topstorweb:/usr/local/apache2/htdocs/ -itd moataznegm/quickstor:git
	docker run -itd --rm --name flask --hostname apisrv -v /etc/localtime:/etc/localtime:ro -v /pace/:/pace -v /pacedata/:/pacedata/ -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -p $myclusterip:5001:5001 -v /TopStor/:/TopStor -v /TopStordata/:/TopStordata moataznegm/quickstor:flask
fi
/TopStor/ioperf.py $etcd $myhost
echo docker exec etcdclient /TopStor/etcdput.py $myclusterip ready/$myhost $mynodeip 
/TopStor/etcdput.py $myclusterip ready/$myhost $mynodeip 
stamp=`date +%s%N`
/pace/etcddel.py $myclusterip sync/ready/Add_${myhost} --prefix
/TopStor/etcdput.py $myclusterip sync/ready/Add_${myhost}_$mynodeip/request ready_$stamp
/TopStor/etcdput.py $myclusterip sync/ready/Add_${myhost}_$mynodeip/request/$leader ready_$stamp
echo running iscsi watchdog daemon
if [ $isprimary -ne 0 ];
then
 echo /pace/iscsiwatchdog.sh $etcd $myhost > /root/iscsiwatch 
 /pace/etcddel.py $mynodeip sync/ready/Add_${myhost} --prefix
else
 /TopStor/etcdput.py $myclusterip nextlead/er $myhost
 /TopStor/etcddel.py $myclusterip sync/nextlead/Add_er_ --prefix
 /TopStor/etcdput.py $myclusterip sync/nextlead/Add_er_${myhost}/request nextlead_$stamp
 /TopStor/etcdput.py $myclusterip sync/nextlead/Add_er_${myhost}/request/$leader nextlead_$stamp
fi
 /pace/syncrequestlooper.sh $leaderip $myhost & disown
 /pace/zfsping.py $leaderip $myhost & disown
 /pace/rebootmeplslooper.sh $leaderip $myhost & disown
 /TopStor/receivereplylooper.sh & disown
 /TopStor/iscsiwatchdog.sh $mynodeip $myhost >/dev/null 2>/dev/null & disown 
 /pace/heartbeatlooper & disown
 /pace/fapilooper.sh & disown

