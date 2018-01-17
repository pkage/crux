##
# Crux data (de)serialization
# @author Patrick Kage

import msgpack

def pack_object(obj):
    return msgpack.packb(obj)

def unpack_object(binary):
    return msgpack.unpackb(obj)

