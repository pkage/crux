##
# Execute a data pipeline
# @author Patrick Kage

import zmq
from crux.common.logging import Logger
from crux.common.exception import CruxException
from crux.common.messaging import Message
from crux.common.validation import version_check
from crux.pipeline.pipeline import Pipeline
from crux.pipeline.component import Component
from crux.backend.daemon_api import DaemonAPI

class PipelineAgentInitError(CruxException):
    pass

class UnmetDependencyError(CruxException):
    pass

class BrokenPipelineError(CruxException):
    pass

class PipelineAgent:
    """Execute a pipeline using the current backend context

    Note that this can be run independently of the backend by specifying your own process pool rather than a daemon address. If a process pool is specified, it will take precedence over the daemon.
    """

    # process pool
    __pool = None
    __daemon_addr = None

    # zmq stuff
    __socket = None
    __context = None

    # daemon api
    __dapi = None

    # components used
    __cpool = None

    # logger
    __log = None

    def __init__(self, daemon_addr=None, context=None, pool=None):
        """Initialize the pipeline agent

        :param daemon_addr: address of the daemon
        :param context: zmq context to use
        :param pool: pool to use if no running daemon
        :raises PipelineAgentInitError: if no process launching mech. exists
        """

        self.__log = Logger(logging=True, name='execpipe')

        # set up context
        if context is None:
            self.__log.warn('initializing a zmq context to connect to {}, this may mean something is wrong!'.format(context))
            self.__context = zmq.Context()
        else:
            self.__context = context

        # set up pooler
        if daemon_addr is not None:
            self.__dapi = DaemonAPI(daemon_addr, context=context)
        elif pool is None:
            raise PipelineAgentInitError('no process launching mechanism provided!')
        else:
            self.__pool = pool

        self.__cpool = {}

    def __process_start(self, path):
        """Start a path using the preferred mechanism

        :param path: path to start
        """
        if self.__dapi is not None:
            return self.__dapi.process_start(path).payload
        else:
            return self.__pool.launch(path)

    def __remap_input(self, inp, remap):
        newinp = {}

        # copy in all the data
        for key in remap:
            newinp[remap[key]] = inp[key]

        # copy in the rest of the input without clobbering the new input
        for key in inp:
            if key not in newinp and key not in remap:
                newinp[key] = inp[key]

        return newinp

    def run(self, pipeline):
        """Run the supplied pipeline

        This function yields every intermediate compuational step.

        :param pipeline: a dictionary object representing a pipeline
        """

        # first set up all required components
        for depname in pipeline['components']:
            dep = pipeline['components'][depname]

            # launch the process, and bind a component handle to it
            addr = self.__process_start(dep['src'])
            self.__cpool[depname] = Component(addr, context=self.__context)

            # check that the dependency satisfies the version requirements
            if not version_check(self.__cpool[depname].cruxfile['version'], dep['version']):
                raise UnmetDependencyError('dependency {}@{} does not match requirement {}'.format(
                    depname,
                    self.__cpool[depname].cruxfile['version'],
                    dep['version']
                ))

        # kick off the pipeline
        inp = {}
        count = 0
        for step in pipeline['pipeline']:
            # perform a request to the specified component
            result = self.__cpool[step['component']].request(Message(
                name='execute',
                payload={
                    'parameters': step['parameters'],
                    'inputs': inp
                }
            ))

            # handle results
            if not result.success:
                # log & fail
                self.__log.error('{}: {}'.format(
                    step['component'],
                    result.payload
                ))
                raise BrokenPipelineError(result.payload)
            else:
                # generators are magic
                yield (count, step, result)
                if 'remap' in step:
                    inp = self.__remap_input(result.payload, step['remap'])
                else:
                    inp = result.payload
                count += 1
        # done!
