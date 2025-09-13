#!/bin/bash

# cloud build runs faster with a single Dockerfile execution

set -e

apt-get update

apt install -y curl git python-is-python3 python3-pip python3.11-venv

python3 -m venv /opt/venv
pip install --upgrade pip

pip install playwright==1.53.0
playwright install --with-deps chromium

cp requirements.txt ./

pip install -r requirements.txt
