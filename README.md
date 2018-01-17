# Crux: A Multipurpose Data Pipeline

## Information

__Author:__ Patrick Kage  
__Version:__ 0.0.2  
__Date:__ 2018-01-16

## Purpose

`crux` is designed to provide a simple but powerful pipeline framework for spacecraft/aero simulations.

## Documentation

### Structure

`crux` provides:

 - a linear data pipeline
 - a component description format
 - autodeployment and management of components via a backend
 - a unified data interchange standard

`crux` sets an environment variable pointing to where to find the crux backend server so components can easily register.

### Client component structure

#### Overview

A `crux` component is made up of:

 - Simulation code
 - Metadata for the crux pipeline

Example `crux` component file tree:

```
client/
├── crux
│   ├── input.json
│   ├── output.json
│   ├── parameters.json
│   └── up.sh
├── crux.json
└── simulation.py
```

#### Crux component file

Should be named `crux.json` and placed in the root of your project directory. This file provides metadata about your project, and provides references to where to find the I/O and parameter configuration files. For example:

```json
{
	"name": "Data Munger",
	"version": "0.0.1",
	"author": "Patrick Kage",
	"description": "an example data-using pipeline component",
	"startup": "sh crux/up.sh",
	"input": "crux/input.json",
	"parameters": "crux/config.json",
	"output": "crux/output.json"
}
```

Note that the `version` field should follow [semantic versioning](https://semver.org). This will be used to ensure client compatibility.

#### Input and Output Schema

Input/output schema are defined as either:

 - JSON output
 - CSV tabular data
 - Raw text
 - Binary

Inputs/outputs are named, and can be remapped by the controller. Here's an example JSON file, describing the different inputs available from the `crux` pipeline:

```json
{
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
```

Output files will look effectively the same, with keys/metadata corresponding . Note that JSON and CSV (tabular) data will be (optionally) schema-validatable, while text and binary I/O will be left to the user. JSON validation should use [JSON Schema](http://json-schema.org/) (explained [here](https://spacetelescope.github.io/understanding-json-schema/)) if applicable.


#### Configuration

Each pipeline component will receive a configuration object from the `crux` pipeline, containing miscellaneous parameters for the execution of that component. Here's an example:

```json
{
	"param1": {
		"name": "An example checkbox parameter",
		"type": "boolean",
		"default": true
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
```

The values of these parameters will be overridden by the client, defaulting to the declared default values.

#### Startup script

The startup script is simply a shell command to execute to start running a component. This can be any shell command, although running a bash script is recommended.

#### Component code

`crux` exposes a client library. Here's an example of how to use it in Python:

```python
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
            sim = Simulation(**config)

            # do some operation to the data
            output = sim.do_some_simulation(data)

            # output that data back to the backend
            cc.output(output)
        except SimulationException ex:
            # handle an error state gracefully
            cc.fail(ex.message)
        except:
            # hard failure
            cc.fail()
    # do cleanup here if necessary
```
