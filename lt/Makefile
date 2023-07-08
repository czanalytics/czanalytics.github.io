# On unique WSL cd <html project>
# make server > make browse 
# 
BROWSER  := google-chrome
BROWSER0 := explorer.exe
URL      := http://0.0.0.0:8000

# python code check 
ruff:
	ruff check .

browse:
	$(BROWSER) $(URL) &

%.ui0 : %.html
	$(BROWSER)  $< 

# sudo kill <PID> # python3
ps:
	pgrep -l -u ah

server:
	python3 -m http.server &
