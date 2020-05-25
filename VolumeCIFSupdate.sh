rm -rf /etc/passwd
rm -rf /etc/group
rm -rf /etc/shadow
ln -s /hostetc/passwd /etc/
ln -s /hostetc/group  /etc/
ln -s /hostetc/shadow  /etc/
