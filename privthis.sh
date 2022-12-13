#!/bin/sh
export ETCDCTL_API=3
cd /TopStor
userpriv='/var/www/html/des20/Data/userpriv.txt';
userreq=` echo $@ | awk '{print $2}'`;
modpriv=` echo $@ | awk '{print $1}'`;
superuser='admin';
sysuser='system';
if [[ $sysuser == $userreq || $superuser == $userreq ]];
then
  echo true;
else
 userinfo=`docker exec etcdclient /TopStor/etcdgetlocal.py usersinfo/$userreq | awk -F"$modpriv" '{print $2}'`
 priv=`echo $userinfo | cut -c 2- |  awk -F'/' '{print $1}'`
 echo $priv | grep 'true' >/dev/null
 if [ $? -eq 0 ];
 then
   echo $priv;
 else
  echo 'false'
 fi
fi
