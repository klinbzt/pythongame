#!/bin/bash

if [ $# -eq 0 ]; then
    echo -e "usage: ./setup.sh [option1] ...\n\n[option1] may include:\n\tcreate - creates the venv\n\tactivate - activates the .venv., (.venv) should appear in front of user prompt.\n\tdelete - deletes the .venv."
    exit 0
fi

if [ "$1" = "delete" ]; then
    rm -r .venv
    exit 0
fi

echo "----------Setup for the python IAp4 project----------"
if [ "$1" = "create" ]; then
    python3 -m venv .venv
    source ./.venv/bin/activate
    sudo apt-get install libsdl2-mixer-2.0-0 libasound2-dev libpulse-dev
    pip3 install -r requirements.txt
    echo "Created virtual environment .venv"
elif [ "$1" = "activate" ]; then
    activdir=$(pwd)
    echo -e "Run this command in your bash to activate the .venv:\n\tsource ./.venv/bin/activate"
    echo -e "\nShould appear (.venv) in front of your user prompt\n |\n |\n \/"
fi