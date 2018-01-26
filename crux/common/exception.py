##
# Crux exception base class
# @author Patrick Kage

class CruxException(Exception):
    """Something broke somewhere"""
    def __init__(self, msg=None):
        self.msg = msg
        if self.msg is None:
            self.msg = 'An unknown error occurred'
        super().__init__(msg)
