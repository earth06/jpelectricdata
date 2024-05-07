#! /bin/bash -l

PYTHON="/home/takato/miniforge3/envs/pi/bin/python"

SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR

$PYTHON scraping_electricity.py > /dev/null 2>&1 
$PYTHON send_to_bluesky.py > /dev/null 2>&1 
