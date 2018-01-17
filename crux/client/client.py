##
# Crux client class
# @author Patrick Kage

import os
import json
import zmq
import msgpack
from crux.common.messaging import Message, MessageException

class InstantiationException(Exception):
    """Something went wrong with instantiating the client"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'Error instantiating crux client!'
        super().__init__(msg)

class NoResultError(Exception):
    """No result has been returned and the socket is in an illegal state"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'No result has been returned!'
        super().__init__(msg)

class CruxClient:
    # zeromq stuff
    __context = None
    __socket = None
    __dirty_socket = False # ;)

    # description stuff
    inputs = None
    outputs = None
    parameters = None
    cruxfile = None

    def __init__(self, description='crux.json', bind=None, context=None):
        """Creates the CruxClient instance

        :param description: where to find the crux description file. defaults to 'crux.json'
        :param bind: the address to bind to. if launched by the crux server, this will be automatically set
        :param context: advanced; specifies a ZMQ context to use (for intra-process comms). if one is not specified, one will be created
        :raises InstantiationException: can fail, error msg will have detail
        """
        # load in all the pieces of the crux description
        with open(description, 'r') as cfile:
            self.cruxfile = json.load(cfile)

            with open(self.cruxfile['input'], 'r') as ifile:
                self.inputs = json.load(ifile)
            with open(self.cruxfile['output'], 'r') as ofile:
                self.outputs = json.load(ofile)
            with open(self.cruxfile['parameters'], 'r') as pfile:
                self.parameters = json.load(pfile)

        # if the bind address is none, assume we're being run by the crux command line client
        # extract the bind address from the environment
        if bind is None:
            if not 'CRUX_BIND' in os.environ:
                raise InstantiationException('no bind address provided and CRUX_BIND unset!')
            bind = os.environ['CRUX_BIND']

        # if the zeromq context is not provided, we'll make our own
        if context is not None:
            self.__context = context
        else:
            self.__context = zmq.Context()

        # make the socket and bind it
        self.__socket = self.__context.socket(zmq.REP)
        self.__socket.bind(bind)

    def __route(self, msg):
        reply = Message()
        # get config or execute
        if msg.name == 'execute':
            return None
        elif msg.name == 'get_config':
            reply.name = 'config'
            reply.payload = self.cruxfile
        elif msg.name == 'shutdown':
            reply.name = 'shutdown'
        else:
            reply.success = False
            reply.name = 'NYI'
        return reply

    def wait(self):
        """Waits for a client to ask something

        :returns: a triple (done status, run config, run inputs)
        """

        while True:
            if self.__dirty_socket:
                raise NoResultError()
            msg = Message(data=self.__socket.recv())
            reply = Message(name='ack')

            # route our reply
            if msg.name == 'execute':
                # this is an execution, pass control back to the main loop (but needing closure)
                self.__dirty_socket = True
                return (False, msg.payload['config'], msg.payload('config'))
            elif msg.name == 'get_config':
                reply.payload = self.cruxfile
            elif msg.name == 'shutdown':
                break
            else:
                # method called has not yet been implemented/is unknown
                reply.name = 'nyi'
                reply.success = False

            # skipped if there was a shutdown or execute instruction
            self.__socket.send(reply.pack())
            self.__dirty_socket = False

        # if we've broken out this side of the loop, assume we're shutting down
        self.__socket.send(reply.pack())
        self.__dirty_socket = False
        return (True, None, None)

    def output(self, output):
        """Returns data to the client

        :param output: the data to send back
        """
        # create the return message
        reply = Message(
            name='return',
            payload=output,
            success=True
        )

        # pack & send off
        self.__socket.send(reply.pack())
        self.__dirty_socket = False

    def fail(self, msg=None):
        """Fail the current operation

        :param msg: An optional message to tell the client what's up
        """

        # create the return message
        reply = Message(
            name='return',
            payload=msg,
            success=False
        )

        # pack & send off
        self.__socket.send(reply.pack())
        self.__dirty_socket = False