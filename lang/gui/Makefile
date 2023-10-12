# Makefile for WSL2 Ubuntu bash-shell 
# 
# Example: cd <project> make server > make browse 
# 
BROWSER  := google-chrome
BROWSER0 := explorer.exe
URL      := http://0.0.0.0:8000
SHELL    := /bin/bash
D = ./tmp

api_status:
	source api.sh && api_status  2>&1 | tee $(D)/log-status.txt

api_report:
	source api.sh && api_report  2>&1 | tee $(D)/log-report.txt

# local targets
all_local: api_status api_report

api_loc1: 
	source api.sh && loc_dict 1.1  1.2  2.2  2.3

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

omega:
	$(BROWSER) $(URL)/omega.html

server:
	python3 -m http.server &

mt:
	$(BROWSER) $(URL)/mt.html &


