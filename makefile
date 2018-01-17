all: build run_concept

run_daemon:
	crux_daemon -b tcp://*:30020 -p tcp://*:30021 --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander:
	harnesses/cmddispatch.py harnesses/testscript.txt

build:
	pip install . --verbose --upgrade
