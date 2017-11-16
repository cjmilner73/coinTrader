#!/bin/bash
IP=$1
echo $IP
scp -i /Users/chrismilner/myKeyPairs/altTrader_key_pair.pem * ec2-user@${IP}:coinTrader
