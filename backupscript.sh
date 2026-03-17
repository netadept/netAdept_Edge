#!/bin/bash

cd ~/netadept

source netadept/bin/activate

cd flask

if [ ! -d "$HOME/netadept/flask/backups" ]; then
  mkdir -p "$HOME/netadept/flask/backups/"
fi   

python scripts/backup.py

cd ~/netadept

deactivate


