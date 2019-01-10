##
# crux main daemon
# @author Patrick Kage

import zmq
from crux.backend.pool import ProcessPool, ProcessLoadError
from crux.common.logging import Logger
from crux.common.messaging import Message
from crux.pipeline.component import Component

class Daemon:
    # zmq stuff
    __context = None
    __apisock = None
    __pubsock = None

    # housekeeping
    __debug = False
    __log = None
    __should_stop = False

    # addresses
    __apisock_addr = None
    __pubsock_addr = None

    # process pool
    __processes = None

    def __init__(self, logging=True, debug=False, bind_addr='tcp://*:30020', pub_addr='tcp://*:30021', context=None, install_loc=None):
        # logging!
        self.__log = Logger(logging=logging, name='daemon')

        # debug mode?
        self.__debug = debug

        # set up the zmq context, re-using if we've got one
        if context is not None:
            self.__context = context
        else:
            self.__context = zmq.Context()

        # set the addresses
        self.__apisock_addr = bind_addr
        self.__pubsock_addr = pub_addr

        # create the API socket
        self.__apisock = self.__context.socket(zmq.REP)
        self.__apisock.bind(self.__apisock_addr)

        # create the publishing socket
        self.__pubsock = self.__context.socket(zmq.PUB)
        self.__pubsock.bind(self.__pubsock_addr)

        # initialize the process pool
        self.__pool = ProcessPool()

        self.__log('initialized daemon')

    def listen(self):
        self.__log.info('daemon listening on {}'.format(self.__apisock_addr))

        # loop until we stop
        while not self.__should_stop:
            message = Message(data=self.__apisock.recv())
            try:
                reply = self.__route(message)
            except Exception as e:
                reply = Message(name='failure', payload='internal error', success=False)
                if self.__debug:
                    self.__log.error(e)
            self.__apisock.send(reply.pack())
        self.__log.warn('stopping daemon!')
        self.__pool.terminate_all()

    def __route(self, msg):
        if msg.name == 'process_start':
            return self.__process_start(msg)
        elif msg.name == 'process_list':
            return self.__process_list(msg)
        elif msg.name == 'process_killall':
            return self.__process_killall(msg)
        elif msg.name == 'daemon_shutdown':
            return self.__shutdown()

        return Message(name='nyi', success=False)

    def __process_start(self, msg):
        if msg.payload is None:
            return Message(name='malformed', success=False)

        path = msg.payload

        try:
            addr = self.__pool.launch(path)
            return Message(name='return', payload=addr)
        except ProcessLoadError as ple:
            return Message(name='failure', success=False, payload=ple.msg)

    def __process_list(self, msg):
        return Message(name='return', payload=self.__pool.get_all_addrs())

    def __process_killall(self, msg):
        self.__log.info('killing all managed processes...')
        self.__pool.terminate_all()
        return Message(name='return')

    def __shutdown(self):
        self.__should_stop = True
        return Message(name='return')

    def __enter__(self):
        pass

    def __exit__(self, e, val, tb):
        """Flushes pool if unclean"""
        print('')
        self.__log.warn('uncleanly flushing pool on shutdown')
        self.__pool.terminate_all()

