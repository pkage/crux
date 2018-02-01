##
# crux client initializer
# @author Patrick Kage

import os
import errno
import getpass
import json

# --- FILES ---
upsh = """#! /bin/sh

cd .. && python simulation.py
"""

simpy = """#! /usr/bin/env python

##
# Crux template component
# @author YOURNAMEHERE
#
# boostrapped with crux create

# import the crux libraries
from crux.client import CruxClient as Crux
from yourcode import Simulation, SimulationException

if __name__ == "__main__":
    # initialize everything
    cc = Crux('crux.json')

    while True:
        # wait for the backend to send some data for processing
        data, config, done = cc.wait()

        if done:
            break

        try:
            # create the simulation from the configuration sent over
            # sim = Simulation(**config)

            # do some operation to the data
            # output = sim.do_some_simulation(data)
            output = {'foo': 'bar', 'baz': [1,2,3]}

            # output that data back to the backend
            cc.output(output)
        except:
            # hard failure
            cc.fail()
    # do cleanup here if necessary
"""

# --- DATA TEMPLATES ---
cruxfile = {
	"name": "datamunger",
	"version": "0.0.1",
	"author": "Patrick Kage",
	"description": "an example data-using pipeline component",
	"startup": "sh crux/up.sh",
	"inputs": "crux/input.json",
	"parameters": "crux/parameters.json",
	"outputs": "crux/output.json"
}

infile = {
	"foo": {
		"type": "json",
		"schema": {}
	},
	"bar": {
		"type": "csv",
		"schema": ["col1", "col2", "col3"]
	},
	"baz": {
		"type": "text"
	},
	"qux": {
		"type": "binary"
	}
}

outfile = {
	"foo": {
		"type": "json",
	},
	"bar": {
		"type": "csv",
	},
	"baz": {
		"type": "text"
	},
	"qux": {
		"type": "binary"
	}
}

paramfile = {
	"param1": {
		"name": "An example checkbox parameter",
		"type": "boolean",
		"default": True
	},
	"param2": {
		"name": "An example text field",
		"type": "text",
		"default": "some text"
	},
	"foo_param": {
		"name": "An example dropdown",
		"type": "dropdown",
		"options": ["option a", "option 1"],
		"default": "option a"
	}
}

def create(name, path=None, author=None):
    if path is None:
        path = os.getcwd()
    elif not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    if author is None:
        author = getpass.getuser()

    # dir structure
    # - (root)
    #    - cruxfile.json
    #    - simulation.py
    #    - crux/
    #        - inputs.json
    #        - outputs.json
    #        - parameters.json
    #        - up.sh

    # configure cruxfile
    global cruxfile
    cruxfile['name'] = name
    cruxfile['author'] = author

    with open(os.path.join(path, 'cruxfile.json'), 'w') as cf:
        json.dump(cruxfile, cf, indent=4)


    # configure simulation.py
    global simpy
    simpy = simpy.replace('YOURNAMEHERE', author)

    with open(os.path.join(path, 'simulation.py'), 'w') as sp:
        sp.write(simpy)

    # make subfolder
    path = os.path.join(path, 'crux')
    os.mkdir(path)

    # add imports/exports/parameters/up.sh
    global infile
    with open(os.path.join(path, 'inputs.json'), 'w') as ij:
        json.dump(infile, ij, indent=4)
    global outfile
    with open(os.path.join(path, 'outputs.json'), 'w') as oj:
        json.dump(outfile, oj, indent=4)
    global paramfile
    with open(os.path.join(path, 'parameters.json'), 'w') as pj:
        json.dump(paramfile, pj, indent=4)
    global upsh
    with open(os.path.join(path, 'up.sh'), 'w') as us:
        us.write(upsh)
