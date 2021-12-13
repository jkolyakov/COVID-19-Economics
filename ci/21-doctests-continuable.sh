#!/bin/sh

set -e

cd /repo

python3 -m doctest -v config.py
python3 -m doctest -v data_management.py
python3 -m doctest -v main.py
python3 -m doctest -v parse_data.py
python3 -m doctest -v process_data.py
