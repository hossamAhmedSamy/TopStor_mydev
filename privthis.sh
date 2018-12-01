#!/bin/sh
export ETCDCTL_API=3
userpriv='/var/www/html/des20/Data/userpriv.txt';
userreq=` echo $@ | awk '{print $2}'`;
modpriv=` echo $@ | awk '{print $1}'`;
superuser='admin';
sysuser='system';
if [[ $sysuser == $userreq || $superuser == $userreq ]];
then
  echo true;
else
 userinfo=`/TopStor/etcdget.py usersinfo/$userreq | awk -F"$modpriv" '{print $2}'`
 priv=`echo $userinfo | cut -c 2- |  awk -F'/' '{print $1}'`
 echo $priv;
fi
