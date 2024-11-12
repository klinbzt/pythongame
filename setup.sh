#!/bin/bash

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment .venv"
fi

source .venv/bin/activate

pip3 install -r requirements.txt
echo "Dependencies installed."