#!/bin/sh
targetcli /iscsi delete iqn.2016-03.com.$1:t1
targetcli /iscsi delete iqn.2016-03.com.$1:data
