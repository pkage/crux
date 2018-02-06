##
# Crux client class
# @author Patrick Kage

import os
import json
import zmq
import msgpack
from crux.common import packing
from crux.common.exception import CruxException
from crux.common.messaging import Message, MessageException
from crux.common.logging import Logger

class InstantiationException(CruxException):
    """Something went wrong with instantiating the client"""

class NoResultError(CruxException):
    """No result has been returned and the socket is in an illegal state"""

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

    # misc housekeeping
    __log = None

    def __init__(self, description='crux.json', bind=None, context=None, logging=True):
        """Creates the CruxClient instance

        :param description: where to find the crux description file. defaults to 'crux.json'
        :param bind: the address to bind to. if launched by the crux server, this will be automatically set
        :param context: advanced; specifies a ZMQ context to use (for intra-process comms). if one is not specified, one will be created
        :param logging: if true, the crux client will log to stdout (on by default)
        :raises InstantiationException: can fail, error msg will have detail
        """

        # create the log object
        self.__log = Logger(logging, name='client')

        # load in all the pieces of the crux description
        self.__log('loading cruxfile {}...'.format(description))
        with open(description, 'r') as cfile:
            self.cruxfile = json.load(cfile)

            with open(self.cruxfile['inputs'], 'r') as ifile:
                self.inputs = json.load(ifile)
                self.cruxfile['inputs'] = self.inputs
            with open(self.cruxfile['outputs'], 'r') as ofile:
                self.outputs = json.load(ofile)
                self.cruxfile['outputs'] = self.outputs
            with open(self.cruxfile['parameters'], 'r') as pfile:
                self.parameters = json.load(pfile)
                self.cruxfile['parameters'] = self.parameters

        # change the log name
        self.__log.set_name(self.cruxfile['name'])
        self.__log('loaded cruxfile (and subfiles) successfully!')

        # if the bind address is none, assume we're being run by the crux command line client
        # extract the bind address from the environment
        if bind is None:
            if not 'CRUX_BIND' in os.environ:
                raise InstantiationException('no bind address provided and CRUX_BIND unset!')
            bind = os.environ['CRUX_BIND']
        self.__log('interpreted bind address as {}'.format(bind))

        # if the zeromq context is not provided, we'll make our own
        if context is not None:
            self.__context = context
        else:
            self.__context = zmq.Context()

        # make the socket and bind it
        self.__socket = self.__context.socket(zmq.REP)
        self.__socket.bind(bind)
        self.__log.info('component listening on {}!'.format(bind))

    def wait(self):
        """Waits for a client to ask something

        :returns: a triple (run inputs, run config, done status)
        """

        while True:
            if self.__dirty_socket:
                raise NoResultError()
            msg = Message(data=self.__socket.recv())
            reply = Message(name='ack')
            self.__log('received {}...'.format(msg.name))

            # route our reply
            if msg.name == 'execute':
                # first check if the request is valid
                if msg.payload is not None and 'parameters' in msg.payload and 'inputs' in msg.payload:
                    # this is an execution, pass control back to the main loop (but needing closure)
                    self.__log('passing execution back...')
                    self.__dirty_socket = True
                    return (
                        packing.unpack_io_object(msg.payload['inputs'], defs=self.cruxfile['inputs']),
                        self.__defaultify(msg.payload['parameters']),
                        False
                    )
                else:
                    reply.name ='malformed'
                    reply.success = False
                    self.__log.error('received malformed execution request')
            elif msg.name == 'get_cruxfile':
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
        self.__log('shutting down loop...')
        self.__socket.send(reply.pack())
        self.__dirty_socket = False
        return (None, None, True)

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
        self.__socket.send(reply.pack(defs=self.cruxfile['outputs']))
        self.__dirty_socket = False
        self.__log('returned output')

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
        self.__log('returned error message')

    def __defaultify(self, parameters):
        """Fill in missing parameters with the defaults

        :param parameters: Parameters recvd. from the requestor
        :returns: filled in parameters
        """

        for param in self.cruxfile['parameters']:
            if 'default' in self.cruxfile['parameters'][param] and (param not in parameters):
                parameters[param] = self.cruxfile['parameters'][param]['default']

        return parameters

