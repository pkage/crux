##
# Crux daemon API
# @author Patrick Kage

import zmq
from crux.common.logging import Logger
from crux.common.messaging import Message

class DaemonAPI:
    # zmq stuff
    __socket = None
    __context = None
    __daemon_addr = None

    # logger
    __log = None

    def __init__(self, daemon_addr, context=None):
        """Initialize the daemon api pointing at a remote API

        :param daemon_addr: the daemon to connect to
        :param context: zmq context to use
        """
        # init logger
        self.__log = Logger(logging=True, name='api_daemon')

        # set up context
        if context is None:
            self.__log.warn('initializing a zmq context to connect to {}, this may mean something is wrong!'.format(context))
            self.__context = zmq.Context()
        else:
            self.__context = context

        # create socket and connect
        self.__daemon_addr = daemon_addr
        self.__socket = self.__context.socket(zmq.REQ)
        self.__socket.connect(self.__daemon_addr)

    def __call(self, msg):
        """Perform remote call

        :param msg: message to send
        """
        self.__socket.send(msg.pack())
        return Message(data=self.__socket.recv())

    def process_start(self, path):
        return self.__call(Message(
            name='process_start',
            payload=path
        ))

    def process_killall(self):
        return self.__call(Message(
            name='process_list'
        ))

    def process_list(self):
        return self.__call(Message(
            name='process_list'
        ))

    def shutdown(self):
        return self.__call(Message(
            name='daemon_shutdown'
        ))
