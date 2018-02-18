all: run_daemon

run_daemon:
	crux_daemon --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander:
	crux repl --script harnesses/testscript.txt

run_pipeline: 
	crux pipeline harnesses/testpipeline.json

run_web:
	crux web

build:
	pip install . --verbose --upgrade

develop:
	python setup.py develop

quick_build:
	pip install . --verbose --upgrade --no-deps

run_web_interface:
	cd dashboard && npm run start

build_web_interface:
	cd dashboard && npm run build
	rm -rf crux/wizards/web/static/
	mv dashboard/build/ crux/wizards/web/static/
