#!/usr/bin/env bash

cd /camera || exit 1
export ENVIRONMENT="prod"
pip install -r requirements.txt
python3 -m waterbowl
