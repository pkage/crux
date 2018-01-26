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

    def unpack(self, data):
        """Unpack some data into this object

        :param data: some msgpack-able data
        """
        try:
            data = packing.unpack_object(data)
        except ValueError:
            raise MessageException('Failed to unpack message!')

        self.name = data['name']
        self.payload = data['payload'] if 'payload' in data else None
        self.success = data['success'] if 'success' in data else True

    def pack(self):
        """Pack this object

        :returns: a binary string containing this message
        """
        if self.name is None:
            # enforce message naming
            raise MessageException('Message must have a name!')

        out = {'name': self.name}
        if self.payload is not None:
            out['payload'] = self.payload
        if self.success is not None:
            out['success'] = self.success

        return packing.pack_object(out)

    def __repr__(self):
        return '<Message name="{}", payload={}, success={}>'.format(
            self.name,
            json.dumps(self.payload) if self.payload is not None else self.payload,
            self.success
        )
