#!/bin/bash

# echo 1 > /wsgi.py
cd ~/railroad-data-pipeline
source .venv/bin/activate
flask scrap

