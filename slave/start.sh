#!/bin/bash

cd /home/rpi/deto
source .venv/bin/activate
python deto_slave.py $(cat id_slave | tr -d '\n')