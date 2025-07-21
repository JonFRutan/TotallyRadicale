#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

#this will create and activate the python environment based on the requirements.txt