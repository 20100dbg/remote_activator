#!/bin/bash

cd /home/marty/deto
source .venv/bin/activate
python deto_slave.py `cat id_slave`