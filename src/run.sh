#! /bin/bash -l


SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  
cd $SCRIPT_DIR

uv run  scraping_electricity.py > $HOME/demand_supply.log 2>&1 
#uv run  send_to_bluesky.py > /dev/null 2>&1 
