#!/bin/bash

ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs kill
ps -ef | grep opt/google/chrome/chrome | grep -v grep | awk '{print $2}' | xargs kill

nohup python3 ./main.py 1 > ./logs/out/scraper.out &
nohup python3 ./main.py 2 > ./logs/out/parser.out &
nohup python3 ./main.py 3 > ./logs/out/enricher.out &
nohup python3 ./main.py 4 > ./logs/out/elastic.out
