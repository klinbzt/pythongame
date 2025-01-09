#!/bin/bash

if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment .venv does not exist."
    exit 1
fi

source .venv/bin/activate

pip3 freeze > requirements.txt
echo "Updated requirements.txt with current dependencies."

deactivate