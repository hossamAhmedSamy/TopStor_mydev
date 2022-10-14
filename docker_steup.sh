myclusterf='/root/topstorwebetc/mycluster'
mynodef='/root/topstorwebetc/mynode'
mynodedev='enp0s8'
myclusterdev='enp0s8'
data1dev='enp0s8'
data2dev='enp0s8'
setenforce 0
echo `hostname` | grep local
if [ $? -eq 0 ];
then
	hostname='dhcp'`echo $RANDOM$RANDOM | cut -c -6`
	hostname $hostname
	echo $hostname > /etc/hostname
	echo InitiatorName=iqn.1994-05.com.redhat:$hostname > /etc/iscsi/initiatorname.iscsi
fi	
targetcli clearconfig confirm=true
nmcli conn delete clusterstub 
nmcli conn delete mynode 
nmcli conn delete mycluster 
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
		nmcli conn add con-name cmynode type ethernet ifname $mynodedev ip4 $mynode ip4 $mycluster
	else
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
systemctl start docker

docker run --rm --name intdns --hostname intdns --net bridge0 -e DNS_DOMAIN=qs.dom -e DNS_IP=10.11.12.7 -e LOG_QUERIES=true -itd --ip 10.11.12.7 -v /root/gitrepo/dnshosts:/etc/hosts moataznegm/quickstor:dns

docker run -itd --rm --name etcd --hostname etcd -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $mynodeip:2397:2397 -v /TopStor/:/TopStor -v /root/etcddata:/default.etcd --net bridge0 moataznegm/quickstor:etcd

docker run -itd --rm --name etcdclient --hostname etcdclient -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -v /TopStor/:/TopStor -v /pace/:/pace moataznegm/quickstor:etcdclient
docker exec -it etcdclient /TopStor/etcdput.py ready/`hostname` $mynodeip 
docker exec -it etcdclient /TopStor/etcdput.py ActivePartners/`hostname` $mynodeip 
docker exec -it etcdclient /TopStor/etcdput.py myhost `hostname` 
docker exec -it etcdclient /TopStor/etcdput.py isprimary `$isprimary` 
/pace/iscsiwatchdog.sh >/dev/null 2>/dev/null & disown 
docker exec  exec etcdclient /TopStor/syncrequest.py >/dev/null 2>/dev/null & disown




#docker run --restart unless-stopped --name git -v /root/gitrepo:/usr/local/apache2/htdocs/ --hostname sgit -p 10.11.11.252:80:80 -v /root/gitrepo/httpd.conf:/usr/local/apache2/conf/httpd.conf -itd -v /root/gitrepo/resolv.conf:/etc/resolv.conf moataznegm/quickstor:git
if [ $isprimary -ne 0 ];
then
	templhttp='/TopStor/httpd_template.conf'
	shttpdf='/TopStor/httpd.conf'
	cp $templhttp $shttpdf
	sed -i "s/MYCLUSTER/$myclusterip/g" $shttpdf
	docker run --rm --name httpd --hostname shttpd --net bridge0 -v /root/gitrepo/resolv.conf:/etc/resolv.conf -p $myclusterip:19999:19999 -p $mynodeip:80:80 -p $mynodeip:443:443 -p $myclusterip:80:80 -p $myclusterip:443:443 -v /TopStor/httpd.conf:/usr/local/apache2/conf/httpd.conf -v /root/topstorwebetc:/usr/local/apache2/topstorwebetc -v /root/topstorweb:/usr/local/apache2/htdocs/ -itd moataznegm/quickstor:git
fi
docker run -itd --rm --name flask --hostname apisrv -v /root/gitrepo/resolv.conf:/etc/resolv.conf --net bridge0 -p $myclusterip:5001:5001 -v /TopStor/:/TopStor -v /root/topstorweb/msgsglobal.txt:/TopStor/msgsglobal.txt -v /root/topstorweb/Data/TopStorglobal.log:/TopStor/TopStorglorbal.log moataznegm/quickstor:flask
