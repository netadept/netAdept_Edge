#!/bin/bash

cd netadept

python3 -m venv netadept

source netadept/bin/activate

pip install -r requirements.txt

cd docker/mongo

docker compose up -d

cd ..

git clone https://github.com/zabbix/zabbix-docker.git

cd zabbix-docker

docker compose up -d




