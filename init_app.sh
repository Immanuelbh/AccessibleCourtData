#!/bin/bash

ps ax | grep main.py | grep -v grep | awk '{print $1}' | xargs kill
ps ax | grep /usr/lib/firefox/firefox | grep -v grep | awk '{print $1}' | xargs kill

nohup python3 ./main.py 1 > ./logs/hcva/scraper.out 2> ./logs/hcva/scraper.err < /dev/null &
nohup python3 ./main.py 2 > ./logs/hcva/parser.out 2> ./logs/hcva/parser.err < /dev/null &
nohup python3 ./main.py 3 > ./logs/hcva/enricher.out 2> ./logs/hcva/enricher.err < /dev/null &
nohup python3 ./main.py 4 > ./logs/hcva/elastic.out 2> ./logs/hcva/elastic.err < /dev/null &
