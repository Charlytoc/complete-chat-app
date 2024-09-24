#!/usr/bin/env bash

set -o errexit

source venv/Scripts/activate

pip install -r requirements.txt

cd ./streaming

npm i

