##
# crux logging facilities
# @author Patrick Kage

from termcolor import colored

# logger class
class Logger:
    logging = False

    def __init__(self, logging=False):
        self.logging = logging

    def log(self, text, level='debug'):
        if not self.logging:
            return
        level = level.lower()

        if level == 'error':
            level = colored('error', 'red')
        elif level == 'warn':
            level = colored('warn ', 'yellow')
        elif level == 'debug':
            level = colored('debug', 'blue')
        else:
            level = colored('info ', 'green')

        print( '[{}]: {}'.format(level, text) )

    def __call__(self, text, level='debug'):
        self.log(text, level)
    def info(self, text):
        self.log(text, level='info')
    def error(self, text):
        self.log(text, level='error')
    def warn(self, text):
        self.log(text, level='warn')
    def debug(self, debug):
        self.log(text, level='debug')

