#! /bin/bash -l


SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR

uv run  scraping_jepx.py > $HOME/log.txt 2>&1 
