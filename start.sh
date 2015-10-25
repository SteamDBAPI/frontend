#!/bin/bash

# Simple script to run flask app as a non-privileged user

#Ex using virtualenv
#dev1:~/frontend$ virtualenv env
#dev1:~/frontend$ source env/bin/activate
#dev1:~/frontend$ pip3 install -r requirements.txt
#dev1:~/frontend$ deactivate

cd /var/www/frontend
sudo -u www-data nohup /var/www/frontend/env/bin/python3 ./serve.py &
