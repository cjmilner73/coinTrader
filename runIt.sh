#!/bin/sh
if ps -ef | grep -v grep | grep coinTrader.py ; then
        exit 0
else
	cd /home/ec2-user/coinTrader && /usr/bin/python /home/ec2-user/coinTrader/coinTrader.py >> /home/ec2-user/coinTrader/log/coinTrader.log 2>&1
        exit 0
fi
