#!/bin/bash

cd ~/netadept

source netadept/bin/activate

cd flask

#gunicorn -w 4 --bind 0.0.0.0:15000 wsgi:app --reload
gunicorn -w 4 --bind 0.0.0.0:15000 -D wsgi:app


### pkill -f gunicorn # to kill process
