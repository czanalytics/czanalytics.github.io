# Makefile for WSL2 Ubuntu bash-shell 
# Some of the targets work in Windows (PowerShell PS> bash.exe) 
#
# Usage: make api_local
#        make api_*
#        make server > make browse 

MAJOR?=0
MINOR?=$(date +%U)
VER=$(MAJOR).$(MINOR)

APP = "lane"
HUB = "czanaytics"
DOCF = "Dockerfile"
IMG = "${APP}"

.PHONY: api-img
api-img:
	@echo "+ $@"
	###docker build -t ${HUB}/${IMG}:${VER} .  -f ./${DOCF} .
	docker build -t lane2 . -f ./Dockerfile
	@echo 'Done.'

BROWSER  := google-chrome
BROWSER0 := explorer.exe
URL      := http://0.0.0.0:8000
SHELL    := /bin/bash
D = ./tmp

api_docker_hub:
	source api.sh && api_docker_hub  2>&1 | tee $(D)/log-docker-hub.txt

api_fuel:
	source api.sh && api_fuel    2>&1 | tee $(D)/log-fuel.txt

api_bundle:
	source api.sh && api_bundle  2>&1 | tee $(D)/log-bundle.txt

api_clean:
	source api.sh && api_clean   2>&1 | tee $(D)/log-clean.txt

api_data:
	source api.sh && api_data    2>&1 | tee $(D)/log-data.txt

api_kb:
	source api.sh && api_kb      2>&1 | tee $(D)/log-kb.txt

api_local:
	source api.sh && api_local   2>&1 | tee $(D)/log-local.txt

api_model:
	source api.sh && api_model   2>&1 | tee $(D)/log-models.txt

api_deploy:
	source api.sh && api_deploy  2>&1 | tee $(D)/log-deploy.txt

api_cloud:
	source api.sh && api_cloud   2>&1 | tee $(D)/log-cloud.txt

api_route:
	source api.sh && api_route   2>&1 | tee $(D)/log-route.txt

api_routing:
	source api.sh && api_routing 2>&1 | tee $(D)/log-routing.txt

api_config:
	source api.sh && api_config  2>&1 | tee $(D)/log-config.txt

api_status:
	source api.sh && api_status  2>&1 | tee $(D)/log-status.txt

api_report:
	source api.sh && api_report  2>&1 | tee $(D)/log-report.txt

# local targets
all_local: api_data api_model api_local api_config api_status api_report

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
