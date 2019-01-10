##
# Crux managed socket
# @author Patrick Kage

import zmq
from crux.common.messaging import Message
from crux.common.exception import CruxException


class RequestTimeoutException(CruxException):
    pass


class ManagedSocket:
    """ManagedSocket

    Wrapper for crux sockets, including Message packets and timeouts
    """
    # the socket
    __socket = None
    __context = None
    __socktype = None
    __address = None

    def __init__(self, context, socktype):
        """Initialize the socket

        :param context: zmq context
        :param socktype: socket type
        """
        self.__context = context
        self.__socktype = socktype
        self.__socket = context.socket(socktype)

    def connect(self, addr):
        """Connect the socket

        :param addr: address to connect to
        """
        self.__address = addr
        self.__socket.connect(addr)
        print('socket is connected to {}'.format(addr))

    def disconnect(self):
        """Disconnect from the address"""
        self.__socket.disconnect(self.__address)

    def send(self, data):
        """Send some data

        :param data: data to send on the socket
        """
        self.__socket.send(data)

    def recv(self, timeout=None):
        """Receive some data on a socket

        If a timeout is specified, then the socket will be cycled

        :param timeout: timeout in milliseconds
        :raises RequestTimeoutException: on timeout
        :returns: Message
        """
        if timeout is None:
            return Message(data=self.__socket.recv())
        else:
            # timeouts get a little hairy, but what we're gonna do is:
            # 1) register socket with a poller
            # 2) send request
            # 3) poll for some amount of time
            # 4) check poller
            # 5) either return or trash the socket
            poll = zmq.Poller()
            poll.register(self.__socket, zmq.POLLIN)

            # poll
            socks = dict(poll.poll(timeout))
            if socks.get(self.__socket):
                ret = Message(data=self.__socket.recv())
                poll.unregister(self.__socket)
                return ret
            else:
                # the socket is broken, trash it
                self.__socket.setsockopen(zmq.LINGER, 0)
                self.__socket.close()
                poll.unregister(self.__socket)

                # create a new socket to replace the old one
                self.__socket = self.__context.socket(self.__socktype)
                self.__socket.connect(self.__address)

                raise RequestTimeoutException('request to {} timed out'.format(address))

    def call(self, message, timeout=None):
        """Perform a Message-wrapped call

        :param message: Message object to send
        :param timeout: in milliseconds
        :raises RequestTimeoutException: on timeout
        """
        self.send(message.pack())
        return self.recv(timeout=timeout)
