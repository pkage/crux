all: build run_concept

run_daemon: build
	crux_daemon --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander:
	harnesses/cmddispatch.py harnesses/testscript.txt

build:
	pip install . --verbose --upgrade
