#!/bin/bash
IP=$1
echo $IP
scp -i /Users/chrismilner/myKeyPairs/altTrader_key_pair.pem /Users/chrismilner/coinTrader/* ec2-user@${IP}:coinTrader/
