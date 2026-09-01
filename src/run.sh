#! /bin/bash -l


SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR
mkdir -p $HOME/logs
uv run  scraping_electricity.py > $HOME/logs/electricscraping.log 2>&1 
#send_to_bluesky.py > /dev/null 2>&1 
