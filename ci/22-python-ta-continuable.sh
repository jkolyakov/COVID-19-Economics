#!/bin/sh

set -e

cd /repo

python_ta config.py \
          data_management.py \
          main.py \
          parse_data.py \
          process_data.py \
          user_interface.py
