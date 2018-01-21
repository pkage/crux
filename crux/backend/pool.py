##
# crux component pool
# @author Patrick Kage

import os
import sys
import uuid
import json
import shlex
import random
import tempfile
import subprocess
from crux.pipeline.component import Component
from crux.common.messaging import Message

class ComponentLoadError(Exception):
    """Something went wrong with loading a component!"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Error handling message!'
        super().__init__(msg)

class ComponentPool:
    """Load and run a pool of components locally"""

    # simple (possibly sub-optimal?) way of holding onto processes
    pool    = {}
    use_ipc = False
    ipc_dir = None

    def __get_temp_dir(self):
        """set up the temp directory we'll use"""
        # osx will use a weird temp dir which i can't be bother with
        tdir = '/tmp/' if sys.platform == 'darwin' else tempfile.gettempdir()

        # create the storage dir if it doesn't exist
        tdir = os.path.join(tdir, 'crux_ipc')
        if not os.path.exists(tdir):
            os.mkdir(tdir)

        return tdir

    def __init__(self, use_ipc=False):
        """Create the pool

        :param use_ipc: whether to use TCP vs socket file transport
        """
        self.use_ipc = use_ipc
        if self.use_ipc:
            self.ipc_dir = self.__get_temp_dir()

    def __convert_bind(self, addr):
        if self.use_ipc:
            return addr
        else:
            # assuming we're only handling local components
            return addr.replace('*', '127.0.0.1')

    def create_bind(self):
        """create a bind address for a component

        :returns: a bindable zmq uri (as a string)
        """
        if self.use_ipc:
            return os.path.join(self.ipc_dir, str(uuid.uuid4()))
        else:
            # this is gross, but should work? there isn't a great way of trying to find a free port
            return 'tcp://*:{}'.format(random.randrange(50000, 65535))

    def launch(self, path, context):
        """Launch a component, and return a pipeline.Component handle

        :param path: path to load (containing cruxfile)
        :param context: the zeromq context to pass to the Component
        :raises ComponentLoadError: on failure to load a component
        :returns: a crux.pipeline.Component, bound, connected, and ready to go
        """

        # attempt to open the cruxfile
        cruxfile = os.path.join(path, 'crux.json')
        if not os.path.exists(cruxfile):
            raise ComponentLoadError('no crux.json in "{}"!'.format(path))

        # parse the cruxfile
        try:
            with open(cruxfile, 'r') as cf:
                cruxfile = json.load(cf)
        except:
            raise ComponentLoadError('unable to parse "{}"!'.format(os.path.join(path, 'cruxfile.json')))

        # double check the cruxfile contains a startup command
        if not 'startup' in cruxfile:
            raise ComponentLoadError('no startup script specified')

        # create a bind address for the component
        bind_addr = self.create_bind()

        # copy the current process's environment variables and patch in a CRUX_BIND
        modified_env = os.environ.copy()
        modified_env['CRUX_BIND'] = bind_addr

        # create the launch command
        launch = shlex.split(cruxfile['startup'])

        # launch
        self.pool[self.__convert_bind(bind_addr)] = subprocess.Popen(
            launch,
            env=modified_env,
            cwd=path
        )

        # wait for the component...
        return Component(self.__convert_bind(bind_addr), context=context)

    def join_all(self):
        for addr in self.pool:
            self.pool[addr].wait()
