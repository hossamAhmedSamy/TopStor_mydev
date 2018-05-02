#!/bin/sh
cd /TopStor
/bin/git branch | grep \* | awk '{print $2}'
