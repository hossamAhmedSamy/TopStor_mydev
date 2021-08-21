#!/bin/sh
targetcli /backstores/iscsi delete iqn.2016-03.com.$1:t1
targetcli /backstores/iscsi delete iqn.2016-03.com.$1:data
