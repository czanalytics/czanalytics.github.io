# Makefile for cza-lang
# 
# Example: cd <project> make server > make browse 
# 
BROWSER  := google-chrome
BROWSER0 := explorer.exe
URL      := http://0.0.0.0:8000
SHELL    := /bin/bash
D = ./log


api_local:
	source api.sh && api_local 2>&1 | tee $(D)/log-local.txt

api_tr:
	source api.sh && api_tr 2>&1 | tee $(D)/log-tr.txt

api_deploy:
	source api.sh && api_deploy  2>&1 | tee $(D)/log-deploy.txt

# local targets
all_local: api_tr api_xx

api_loc1: 
	source api.sh && loc_dict 1.1  1.2  2.2  2.3

api_loc2: 
	source api.sh && loc_dict 1.11 1.22 2.22 2.33

# make str=cza grep
grep: 
	grep -r $(str) *

test:
	python3 test.py

# python code check 
ruff:
	ruff check .

browse:
	$(BROWSER) $(URL) &

%.ui0 : %.html
	$(BROWSER)  $< 

# kill <PID> or sudo kill <PID> # 'python3' locates bg server
ps:
	pgrep -l -u ah

server:
	python3 -m http.server &
