rm -rf /etc/passwd
rm -rf /etc/group
rm -rf /etc/shadow
ln -s /hosetc/passwd /etc/passwd
ln -s /hosetc/passwd /etc/group
ln -s /hosetc/passwd /etc/shadow
