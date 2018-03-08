##
# Crux component descriptor
# @author Patrick Kage

import json
import zmq
from crux.common.socket import ManagedSocket
from crux.common.logging import Logger
from crux.common.messaging import Message


class Component:
    """A description of a running crux component"""
    # description
    cruxfile  = None
    address   = None

    # zmq stuff
    __socket  = None
    __context = None

    # housekeeping
    __log     = None

    def __init__(self, address, socket=None, context=None, timeout=None):
        """Initialize the component

        :param address: the address of the component
        :param socket: the socket to use for communication, if we're sharing (one will be created if not provided)
        :param timeout: timeout for resolving the component
        :param context: the context to use to create a socket (if no socket provided), one will be created if not used
        """
        # logging?
        self.__log = Logger(logging=True)

        # set up the ZMQ stuff
        if context is None:
            if socket is None:
                self.__log.warn('creating new zmq context for component! something is probably wrong')
                self.__context = zmq.Context()
        else:
            self.__context = context

        # if we haven't got a socket yet, get one
        self.__socket = ManagedSocket(self.__context, zmq.REQ)

        # connect the socket
        self.__log('connecting to {}'.format(address))
        self.__socket.connect(address)

        # get the cruxfile
        self.cruxfile = self.request(Message(name='get_cruxfile'), timeout=timeout).payload

    def request(self, msg, timeout=None):
        """Do a request on this component

        :param msg: the message to post to the client
        :param timeout: timeout in ms
        :returns: the reply
        """
        return self.__socket.call(msg, timeout=timeout)


