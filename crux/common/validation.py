##
# Crux data validation
# @author Patrick Kage

import os
import semver
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError as ve

def version_check(candidate, constraint):
    """Ensure that a candidate component version matches a constraint (semver)

    :param candidate: the candidate to drop in
    :param constraint: version constraint
    """
    return semver.match(candidate, constraint)

def validate_schema(schema_file, instance):
    """
    Validate json instance based on schema contained in schema_file. Need schema_file as opposed to loaded schema because we use the path of the schema file to resolve $ref's within it.

    :param schema_file: absolute path of schema file (including the file name)
    :param instance: loaded json instance
    :return: True if instance is valid, False
    """

    if not os.path.exists(schema_file):
        raise RuntimeError('Specified schema file does not exist: %s'%(schema_file))

    schema_path = os.path.dirname(schema_file)

    schema_uri = 'file:///{0}/'.format(schema_path)
    resolver = RefResolver(schema_uri, schema_file)

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    try:
        # note returns None. Raises errors to indicate invalidity
        validate(instance, schema, resolver=resolver)
    except ve as e:
        # TODO: what should we actually do here. Pass an exception up?
        print('saw jsonschema.exceptions.ValidationError')
        print('e.message')
        print(e.message)

        if args.verbose:
            print('e.schema')
            print(e.schema)
            print('e.instance')
            print(e.instance)
            print('e.cause')
            print(e.cause)
            print('e.context')
            print(e.context)

        return False

    return True




if __name__ == "__main__":
    import argparse
    import json

    # Define parser for command line arguments
    ap = argparse.ArgumentParser(description='tool for validating a .json file per its corresponding schema')
    ap.add_argument("schema_file",
                    help='.json schema_file file that specifices the schema from which to validate. \
    	Either name of file within same dir as this script, or a file name preceded by absolute path')
    ap.add_argument("instance_file",
                    help='.json instance_file file that specifices the schema instance to be validated \
    	Either name of file within same dir as this script, or a file name preceded by absolute path')
    ap.add_argument('-v', '--verbose',
                    action='store_true',
                    help='controls verbosity of script')

    # Parse the command line arguments
    args = ap.parse_args()

    schema_file = args.schema_file
    instance_file = args.instance_file

    if not os.path.exists(schema_file):
        raise RuntimeError('Specified schema file does not exist: %s' % (schema_file))
    if not os.path.exists(instance_file):
        raise RuntimeError('Specified instance file does not exist: %s' % (schema_file))

    with open(instance_file, 'r') as f:
        instance = json.load(f)

    # make sure we have the absolute path
    schema_file = os.path.abspath(schema_file)

    valid = validate_schema(schema_file, instance)

    if valid:
        print('Passed')


