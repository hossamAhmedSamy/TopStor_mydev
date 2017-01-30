#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
declare -a targets=(`cat /pacedata/iscsitargets | awk '{print $2}'`);
#node=`echo $@ | awk '{print $1}'`
#node=`hostname -s`
if [ ! -f /root/.ssh/id_rsa ] ;then 
 ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P "";
fi
for node in "${targets[@]}"; do
securessh=$(expect -c "
 set timeout 10
 spawn ssh-copy-id -i /root/.ssh/id_rsa.pub root@$node 
 expect \"*\?\"
send \"yes\r\"
expect \"*assword:\"
send \"YousefNadody\r\"
expect eof
")
done
