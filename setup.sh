#!/bin/bash

cd netadept

python3 -m venv netadept

source netadept/bin/activate

pip install -r requirements.txt

### Install MongoDB ###

cd docker/mongo

docker compose up -d

cd ..

### Install Zabbix ###

git clone https://github.com/zabbix/zabbix-docker.git

cd zabbix-docker

docker compose up -d

cd ~

### Install GoTTY ###

wget -qO gotty.tar.gz https://github.com/yudai/gotty/releases/latest/download/gotty_linux_amd64.tar.gz

sudo tar xf gotty.tar.gz -C /usr/local/bin

rm -rf gotty.tar.gz

### Install SSHPass ###

sudo apt update && sudo apt install sshpass -y



