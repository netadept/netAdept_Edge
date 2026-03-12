#!/bin/bash

cd netadept

source netadept/bin/activate

cd flask

python scripts/backup.py
