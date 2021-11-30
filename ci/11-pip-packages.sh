#!/bin/sh

set -e

cd /repo

pip3 install -r requirements.txt
pip3 install -r requirements_dev.txt
