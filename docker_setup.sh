myclusterf='/topstorwebetc/mycluster'
mynodef='/topstorwebetc/mynode'
myhost=`hostname`
targetcli clearconfig confirm=True	
echo ${myhost}$@ | egrep 'init|local'
if [ $? -eq 0 ];
then
	myhost='dhcp'`echo $RANDOM$RANDOM | cut -c -6`
	hostname $myhost
	echo $myhost > /etc/hostname
	echo InitiatorName=iqn.1994-05.com.redhat:$myhost > /etc/iscsi/initiatorname.iscsi
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
			rm  -rf /root/etcddata/* 
			docker run --rm --name intdns --hostname intdns --net bridge0 -e DNS_DOMAIN=qs.dom -e DNS_IP=10.11.12.7 -e LOG_QUERIES=true -itd --ip 10.11.12.7 -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/dnshosts:/etc/hosts moataznegm/quickstor:dns
			docker run -itd --rm --name etcd --hostname etcd -v /root/gitrepo/resolv.conf:/etc/resolv.conf -v /TopStor/:/TopStor -v /root/etcddata:/default.etcd --net bridge0 moataznegm/quickstor:etcd
docker run -itd --rm --name etcdclient --hostname etcdclient -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:etcdclient 
			started=0
        		while [ $started -eq 0 ];
        		do
                		docker logs etcd | grep 'successfully notified init daemon'
                		if [ $? -eq 0 ];
                		then
                        		started=1
                		else
                        		sleep 1
                		fi
        		done

			docker exec etcdclient /TopStor/UnixsetUser.py etcd `hostname` admin tmatem
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
	eth1=$1
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
nmcli conn add con-name clusterstub type ethernet ifname $myclusterdev ip4 169.168.12.12 
nmcli conn up clusterstub
nmcli conn up mynode
nmcli conn delete cmynode
nmcli conn delete cmycluster
isinitn=`nmcli conn show | grep mynode | wc -c`
if [ $isinitn -le 5 ];
then
	mynode='10.11.11.244/24'
	nmcli conn add con-name mynode type ethernet ifname $mynodedev ip4 $mynode
	targetcli clearconfig confirm=True	
	targetcli saveconfig 
else
	mynode=`nmcli conn show mynode | grep ipv4.addresses | awk '{print $2}'`
fi
isinitn=`nmcli conn show | grep mycluster | wc -c`
if [ $isinitn -le 5 ];
then
	mycluster='10.11.11.250/24'
	nmcli conn add con-name mycluster type ethernet ifname $myclusterdev ip4 $mycluster

else
	mycluster=`nmcli conn show mycluster | grep ipv4.addresses | awk '{print $2}'`
fi

mynodeip=`echo $mynode | awk -F'/' '{print $1}'`
myip=$mynodeip
myclusterip=`echo $mycluster | awk -F'/' '{print $1}'`
ping -w 3 $myclusterip 
if [ $? -ne 0 ];
then 
	isprimary=1
else
	isprimary=0
fi
echo $mynodedev | grep $myclusterdev
if [ $? -eq 0 ];
then
	if [ $isprimary -ne 0 ];
	then
		echo I am prmary
		nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode ip4 $mycluster
	else
		echo I am a cluster node 
		nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode
	fi
else
	nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode
	nmcli conn add con-name cmycluster type ethernet ifname $myclusterdev ip4 $mycluster
	if [ $isprimary -ne 0 ];
	then
		nmcli conn up cmycluster
	fi

fi
nmcli conn up cmynode
systemctl start target
systemctl start iscsid 
systemctl start docker

docker run --rm --name intdns --hostname intdns --net bridge0 -e DNS_DOMAIN=qs.dom -e DNS_IP=10.11.12.7 -e LOG_QUERIES=true -itd --ip 10.11.12.7 -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/dnshosts:/etc/hosts moataznegm/quickstor:dns
if [ $isprimary -eq 1 ];
then
	etcd=$myclusterip
	leader=$myhost
	leaderip=$myclusterip
else
	etcd=$mynodeip
fi
docker run -itd --rm --name etcd --hostname etcd -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $etcd:2379:2379 -v /TopStor/:/TopStor -v /root/etcddata:/default.etcd --net bridge0 moataznegm/quickstor:etcd
docker run -itd --rm --name etcdclient --hostname etcdclient -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:etcdclient 
#docker run -d --rm --name rmq --hostname rmq  -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -p $etcd:5672:5672 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:rabbitmq 
systemctl start rabbitmq-server
rabbitmqctl add_user rabb_Mezo YousefNadody 2>/dev/null
rabbitmqctl set_permissions -p / rabb_Mezo ".*" ".*" ".*" 2>/dev/null
started=0
while [ $started -eq 0 ];
do
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
		echo docker exec etcdclient /pace/etcdput.py $myclusterip clusternode $myhost
		echo isprimary $isprimary >> /root/dockerlogs.txt
		docker exec etcdclient /TopStor/etcdput.py $myclusterip ActivePartners/$myhost $mynodeip 
		docker exec etcdclient /TopStor/etcdput.py $myclusterip leaderip $myclusterip 
		echo docker exec  etcdclient /TopStor/etcdput.py $myclusterip leaderip $myclusterip >> /root/dockerlogs.txt
		docker exec etcdclient /TopStor/etcdput.py $myclusterip leader $myhost 
		docker exec etcdclient /TopStor/etcdput.py $myclusterip nextlead/er 'None' 

	else
		echo docker exec etcdclient /pace/etcdget.py $myclusterip clusternode
		echo isprimaryin0 $isprimary >> /root/dockerlogs.txt
		docker exec etcdclient /pace/etcdget.py $myclusterip Active --prefix | grep $myhsot
		if [ $? -ne 0 ];
		then
			docker exec etcdclient /TopStor/etcdput.py $myclusterip possible$myhost $mynodeip 
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
			fi
		done
		stamp=`date +%s%N`

		myalias=`docker exec etcdclient /pace/etcdget.py $mynodeip $aliast/$myhost`
		docker exec etcdclient /pace/etcddel.py $myip leader --prefix
		leader=`docker exec etcdclient /pace/etcdget.py $myclusterip leader`
		docker exec etcdclient /pace/etcdput.py $myip clusternode $myhost
		docker exec etcdclient /pace/etcddel.py $myip sync/pools request/$myhost 2>/dev/null
		docker exec etcdclient /pace/etcddel.py $myip sync/Snapperiod/initial $myhost request/$myhost 2>/dev/null
        	docker exec etcdclient /pace/etcddel.py $myip pools --prefix 2>/dev/null
		docker exec etcdclient /pace/etcddel.py $myip volumes --prefix 2>/dev/null
		docker exec etcdclient /pace/etcddel.py $myip sync/pools Add_ 2>/dev/null
		docker exec etcdclient /pace/etcddel.py $myip sync/pools Del_ 2>/dev/null
		docker exec etcdclient /pace/etcddel.py $myip sync/volumes  2>/dev/null
        	docker exec etcdclient /pace/etcdput.py $myclusterip $aliast/$myhost $myalias
		/TopStor/syncq.py $myclusterip $myhost 2>/root/syncqerror
		myalias=`echo $myalias | sed 's/\_/\:\:\:/g'`
		docker exec etcdclient /pace/etcdput.py $myclusterip sync/$aliast/Add_${myhost}_$myalias/request ${aliast}_$stamp.
		docker exec etcdclient /pace/etcdput.py sync/$aliast/Add_${myhost}_$myalias/request/$myhost ${aliast}_$stamp.
		issync=`docker exec etcdclient /pace/etcdget.py $myip sync initial`initial
		echo $issync | grep $myhost
		if [ $? -eq 0 ];
		then
	    	echo syncrequests only
    			docker exec etcdclient /pace/checksyncs.py syncrequest $mycluster $myclusterip $myhost $myip
       		else
			echo have to syncall
			docker exec etcdclient /pace/checksyncs.py syncall $mycluster $myclusterip $myhost $myip
		fi
	fi
	checkcluster=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
	echo $checkcluster >> /root/dockerlogs.txt
	echo hihi$checkcluster | grep $myclusterip
done
#############################3
zpool export -a
docker exec etcdclient /TopStor/etcdput.py $etcd mynodeip $mynodeip 
docker exec etcdclient /TopStor/etcdput.py $etcd mynode $mynode 
docker exec etcdclient /TopStor/etcdput.py $etcd myclusterip $myclusterip 
docker exec etcdclient /TopStor/etcdput.py $etcd isprimary $isprimary 
rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
if [ $isprimary -eq 1 ];
then
	echo docker exec etcdclient /pace/checksyncs.py syncinit $leader $etcd $myhost $etcd
	docker exec etcdclient /pace/checksyncs.py syncinit $leader $etcd $myhost $etcd
fi
 /TopStor/topstorrecvreply.py $etcd & disown
/pace/syncrequestlooper.sh $etcd $mynodeip >/dev/null 2>/dev/null & disown 
/pace/iscsiwatchdog.sh $etcd >/dev/null 2>/dev/null & disown 
docker exec -it etcdclient /TopStor/etcdput.py $etcd ready/$myhost $mynodeip 



#docker run --restart unless-stopped --name git -v /root/gitrepo:/usr/local/apache2/htdocs/ --hostname sgit -p 10.11.11.252:80:80 -v /root/gitrepo/httpd.conf:/usr/local/apache2/conf/httpd.conf -itd -v /root/gitrepo/resolv.conf:/etc/resolv.conf moataznegm/quickstor:git
if [ $isprimary -ne 0 ];
then
	templhttp='/TopStor/httpd_template.conf'
	shttpdf='/TopStor/httpd.conf'
	cp $templhttp $shttpdf
	sed -i "s/MYCLUSTER/$myclusterip/g" $shttpdf
	docker run --rm --name httpd --hostname shttpd --net bridge0 -v /etc/localtime:/etc/localtime:ro -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $myclusterip:19999:19999 -p $mynodeip:80:80 -p $mynodeip:443:443 -p $myclusterip:80:80 -p $myclusterip:443:443 -v /TopStor/httpd.conf:/usr/local/apache2/conf/httpd.conf -v /root/topstorwebetc:/usr/local/apache2/topstorwebetc -v /topstorweb:/usr/local/apache2/htdocs/ -itd moataznegm/quickstor:git
fi
docker run -itd --rm --name flask --hostname apisrv -v /etc/localtime:/etc/localtime:ro -v /pace/:/pace -v /pacedata/:/pacedata/ -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -p $myclusterip:5001:5001 -v /TopStor/:/TopStor -v /TopStordata/:/TopStordata moataznegm/quickstor:flask
/TopStor/ioperf.py $etcd $myhost
docker exec etcdclient /TopStor/etcdput.py $etcd ready/$myhost $mynodeip 
stamp=`date +%s%N`
docker exec etcdclient /TopStor/etcdput.py $etcd sync/ready/Add_$myhost_$mynodeip/request ready_$stamp
docker exec etcdclient /TopStor/etcdput.py $etcd sync/ready/Add_$myhost_$mynodeip/request/$leader ready_$stamp

