#!/bin/bash

docker run -v $(pwd)/data:/data cs408-lab2 python3 /grade.py -s /submissions -d /data/$1 -t /tests/$1