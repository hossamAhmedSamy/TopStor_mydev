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
 userinfo=`/TopStor/etcdget.py usersinfo/$userreq | awk -F"$modpriv" '{print $2}'`
 priv=`echo $userinfo | cut -c 2- |  awk -F'/' '{print $1}'`
 echo $priv | grep 'true' >/dev/null
 if [ $? -eq 0 ];
 then
  ./UnixChkUser2 $userreq 'cheking'
  x=`./etcdget.py logged/$userreq | wc -c`
  if [ x -gt 5 ];
  then
   echo $priv;
  else
   echo 'false'
  fi
 else
  echo 'false'
 fi
fi
