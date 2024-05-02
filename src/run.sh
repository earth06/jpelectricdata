#! /bin/bash

PYTHON="xxxxx"

SCRIPT_DIR=$(cd $(dirname $0); pwd -P)  

python scraping_electricity.py
python send_to_bluesky.py