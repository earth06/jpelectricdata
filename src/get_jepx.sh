#! /bin/bash -l


SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR

mkdir -p $HOME/logs
uv run  scraping_jepx.py > $HOME/logs/log.txt 2>&1 
