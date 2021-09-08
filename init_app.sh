#!/bin/bash

ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep opt/google/chrome/chrome | grep -v grep | awk '{print $2}' | xargs kill

nohup python3 ./main.py 1 > ./logs/hcva/scraper.out &
nohup python3 ./main.py 2 > ./logs/hcva/parser.out &
nohup python3 ./main.py 3 > ./logs/hcva/enricher.out &
nohup python3 ./main.py 4 > ./logs/hcva/elastic.out
