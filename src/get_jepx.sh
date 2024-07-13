#! /bin/bash -l

PYTHON="/home/takato/miniforge3/envs/pi/bin/python"

SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR

$PYTHON scraping_jepx.py > /home/takato/mnt/tmp/log.txt 2>&1 
