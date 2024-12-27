#! /bin/bash

RUNPYTHON=/home/takato/uvpy312/bin/python
SCRIPT_DIR=$(cd $(dirname $0); pwd -P)

cd $SCRIPT_DIR/app 
$RUNPYTHON app.py --host  100.66.1.13 --port 8049  2>&1  > /dev/null

