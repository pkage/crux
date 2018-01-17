##
# crux logging facilities
# @author Patrick Kage

from termcolor import colored

# logger class
class Logger:
    logging = False
    filt = None

    def __init__(self, logging=False, filt=None):
        self.logging = logging
        self.filt = filt

    def log(self, text, level='debug'):
        if not self.logging or self.__filtered(level):
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

    def __filtered(self, level):
        levels = ['debug', 'info', 'warn', 'error']
        if self.filt == None or not level in levels:
            return False
        return levels.index(self.filt) >= levels.index(level)


