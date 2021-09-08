#!/bin/bash

ps ax | grep main.py | grep -v grep | awk '{print $1}' | xargs kill
ps ax | grep /usr/lib/firefox/firefox | grep -v grep | awk '{print $1}' | xargs kill