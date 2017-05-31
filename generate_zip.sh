#!/bin/bash
cd ./lib/python3.5/site-packages/ && zip -r9 ../../../josh.zip *
cd ../../../josh && zip -g ../josh.zip model.py scheduler.py response.py infrastructure.py generate_uid.py
