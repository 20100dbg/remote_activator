#!/bin/bash
cd /home/rpi/deto
source .venv/bin/activate
gunicorn --worker-class gevent -w 1 app:app --bind 0.0.0.0:5000