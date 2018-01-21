##
# Crux data validation
# @author Patrick Kage

import semver
import jsonschema

def version_check(candidate, constraint):
    """Ensure that a candidate component version matches a constraint (semver)

    :param candidate: the candidate to drop in
    :param constraint: version constraint
    """
    return semver.match(candidate, constraint)

def validate_schema(schema, target):
    # not a solution
    return True
