##
# crux component process pool
# @author Patrick Kage

import os
import sys
import uuid
import json
import shlex
import random
import tempfile
import subprocess
from crux.common.messaging import Message
from crux.common.exception import CruxException
from crux.pipeline.component import Component

class ProcessLoadError(CruxException):
    pass

class ProcessPool:
    """Load and run a pool of components as local processes"""

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
        """Convert a bind address to a connect-able address. IPC-aware

        :param addr: address to convert
        """
        if self.use_ipc:
            return addr
        else:
            # assuming we're only handling local components
            return addr.replace('*', '127.0.0.1')

    def __create_bind(self):
        """create a bind address for a component

        :returns: a bindable zmq uri (as a string)
        """
        if self.use_ipc:
            return 'ipc://{}'.format(os.path.join(self.ipc_dir, str(uuid.uuid4())))
        else:
            # this is gross, but should work? there isn't a great way of trying to find a free port
            return 'tcp://*:{}'.format(random.randrange(50000, 65535))

    def launch(self, path):
        """Launch a component, and return a address to connect to the component at

        :param path: path to load (containing cruxfile)
        :param context: the zeromq context to pass to the Component
        :raises ProcessLoadError: on failure to load a component
        :returns: a crux.pipeline.Component, bound, connected, and ready to go
        """

        # attempt to open the cruxfile
        cruxfile = os.path.join(path, 'crux.json')
        if not os.path.exists(cruxfile):
            raise ProcessLoadError('no crux.json in "{}"!'.format(path))

        # parse the cruxfile
        try:
            with open(cruxfile, 'r') as cf:
                cruxfile = json.load(cf)
        except:
            raise ProcessLoadError('unable to parse "{}"!'.format(os.path.join(path, 'cruxfile.json')))

        # double check the cruxfile contains a startup command
        if not 'startup' in cruxfile:
            raise ProcessLoadError('no startup script specified')

        # create a bind address for the component
        bind_addr = self.__create_bind()

        # copy the current process's environment variables and patch in a CRUX_BIND
        modified_env = os.environ.copy()
        modified_env['CRUX_BIND'] = bind_addr

        # change the bind addr into an address to connect to
        connect_addr = self.__convert_bind(bind_addr)

        # create the launch command
        launch = shlex.split(cruxfile['startup'])

        # launch
        self.pool[connect_addr] = subprocess.Popen(
            launch,
            env=modified_env,
            cwd=path
        )

        # this can be passed right into a component constructor
        return connect_addr

    def join_all(self):
        """Wait for all managed processes to exit on their own"""
        for addr in self.pool:
            self.pool[addr].wait()

    def kill_all(self):
        """Send SIGKILL on all managed processes"""
        for addr in self.pool:
            self.pool[addr].kill()

    def terminate_all(self):
        """Send SIGTERM to all managed processes

        On Windows, this has the same effect as ComponentPool.kill_all()
        """
        for addr in self.pool:
            self.pool[addr].terminate()

    def get_all_addrs(self):
        """Get all addresses for all processes managed by this pool

        :returns: a list of addresses
        """
        self.poll_all()
        return [addr for addr in self.pool]

    def poll_all(self):
        """Poll all managed processes and remove stopped ones"""
        deadprocs = []
        for addr in self.pool:
            if self.pool[addr].poll() is not None:
                deadprocs.append(addr)

        for addr in deadprocs:
            del self.pool[addr]
