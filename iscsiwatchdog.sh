#!/usr/bin/sh
cd /pace/
lsscsi=0
#dmesg -n 1
rabbitip=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
iscrashed=`echo $@ | awk '{print $3}'`
echo param $rabbitip , $myhost, $iscrashed
echo start >> /root/iscsiwatch
targetn=0
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
leaderip=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
myhostip=$rabbitip
echo $leader | grep $myhost
if [ $? -eq 0 ];
then
	initip=1
else
 	initip=3
fi
echo $iscrashed | grep 0
if [ $? -eq 0 ];
then
 initipstatus=`docker ps` 
 echo $initipstatus | grep 8080
 if [ $? -eq 0 ];
 then
  echo $initipstatus | grep $myhostip
  if [ $? -eq 0 ];
  then
   initip=4
  else
   initip=2
  fi
 fi
fi
initstamp=`date +%s`
echo $initstamp > /TopStordata/initstamp
isinitn=`cat /root/nodeconfigured`'s'
echo $isinitn | grep 'yess'
if [ $? -ne 0 ];
then
 /pace/senddiscovery.sh & disown
fi
while true;
do
	leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
	echo $leader | grep $myhost
	if [ $? -eq 0 ];
	then
		etcdip=$leaderip
	else
		etcdip=$myhostip
	fi
	lsscsinew=`lsscsi -is | wc -c `
	cd /pace
	if [ $lsscsinew -ne $lsscsi ];
	then
		lsscsi=$lsscsinew
		/pace/addtargetdisks.sh $etcdip $myhost
		/pace/iscsirefresh.sh $etcdip $myhost
		/pace/listingtargets.sh $etcdip
		/TopStor/etcdput.py $etcdip dirty/pool 0
	fi
	targetnewn=`targetcli ls | wc -c`
	if [ $targetnewn -ne $targetn ];
	then
		targetn=$targetnewn
		lsscsi=0

	fi
        /pace/putzpool.py $leader $leaderip $myhost $myhostip 
	echo '###############################################################'
	echo initip $initip
	if [ $initip -eq 1 ];
	then
		
	echo '###############################################################'
	echo adding 254 and docker
		stamp=`date +%s`
		stamp=$((stamp+300))
		nmcli conn mod cmynode +ipv4.addresses 10.11.11.254/24
		nmcli conn up cmynode
		/TopStor/httpdflask.sh $rabbitip yes
		initip=2
	fi
	if [ $initip -eq 2 ];
	then
		stamp2=`date +%s`
		if [ $stamp2 -ge $stamp ];
		then
			docker rm -f httpd_local
			nmcli conn mod cmynode -ipv4.addresses 10.11.11.254/24
			nmcli conn up cmynode
			initip=3
		fi
	fi
	if [ $initip -eq 3 ];
	then
			/TopStor/httpdflask.sh $rabbitip no 
			initip=4
	fi

	echo sleeeeeeeeeeeeeping
	sleep 2
	echo cyclingggggggggggggg
done
