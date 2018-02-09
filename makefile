all: build run_concept

run_daemon: build
	crux_daemon --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander:
	crux repl --script harnesses/testscript.txt

run_pipeline: 
	crux pipeline harnesses/testpipeline.json

run_web: quick_build
	crux web

build:
	pip install . --verbose --upgrade

quick_build:
	pip install . --verbose --upgrade --no-deps

build_web_interface:
	cd dashboard && npm run build
	rm -rf crux/wizards/web/static/
	mv dashboard/build/ crux/wizards/web/static/
