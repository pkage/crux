all: build run_concept

run_daemon: build
	crux_daemon --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander:
	crux repl --script harnesses/testscript.txt

run_pipeline: 
	harnesses/launchpipeline.py harnesses/testpipeline.json

build:
	pip install . --verbose --upgrade
