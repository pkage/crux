all: run_daemon

run_daemon: quick_build
	crux_daemon --logging --debug

run_concept:
	cd examples/client/ && CRUX_BIND="tcp://*:30020" python simulation.py

run_commander: quick_build
	crux repl --script harnesses/testscript.txt

run_pipeline: quick_build
	crux pipeline harnesses/testpipeline.json

run_web: quick_build
	crux web

build:
	pip install . --verbose --upgrade --retries 0

build-webdebug:
	pip install .[webdebug] --verbose --upgrade

develop:
	python setup.py develop

quick_build:
	pip install . --verbose --upgrade --no-deps --retries 0

run_web_interface:
	cd dashboard && npm run start

build_web_interface:
	cd dashboard && npm run build
	rm -rf crux/wizards/web/static/
	mv dashboard/build/ crux/wizards/web/static/
