##
# Crux inter-agent messaging
# @author Patrick Kage

import json
import msgpack
from crux.common import packing
from crux.common.exception import CruxException

class MessageException(CruxException):
    pass

class Message:
    """Message class to facilitate messaging between all crux components"""
    name = None
    payload = None
    success = None

    def __init__(self, data=None, name=None, payload=None, success=None):
        if name is not None:
            self.name = name
            if payload is not None:
                self.payload = payload
            if success is not None:
                self.success = success
        elif data is not None:
            self.unpack(data)

    def unpack(self, data, defs=None):
        """Unpack some data into this object

        :param data: some msgpack-able data
        :param defs: If not none, unpack this obj efficiently according to the definitions
        """
        try:
            data = packing.unpack_object(data)
        except ValueError:
            raise MessageException('Failed to unpack message!')

        self.name = data['name']
        self.success = data['success'] if 'success' in data else True
        if 'payload' in data:
            if defs is None:
                self.payload = data['payload']
            else:
                self.payload = packing.unpack_io_object(data['payload'], defs)
        else:
            self.payload = None

    def pack(self, defs=None):
        """Pack this object

        :param defs: If not none, pack this obj efficiently according to the definitions
        :returns: a binary string containing this message
        """
        if self.name is None:
            # enforce message naming
            raise MessageException('Message must have a name!')

        out = {'name': self.name}
        if self.payload is not None:
            if defs is None:
                out['payload'] = self.payload
            else:
                out['payload'] = packing.pack_io_object(self.payload, defs)
        if self.success is not None:
            out['success'] = self.success

        return packing.pack_object(out)

    def __repr__(self):
        return '<Message name="{}", payload={}, success={}>'.format(
            self.name,
            json.dumps(self.payload) if self.payload is not None else self.payload,
            self.success
        )
