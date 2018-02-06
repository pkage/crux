##
# Crux data (de)serialization
# @author Patrick Kage

import io
import csv
import msgpack
import binascii

def pack_object(obj):
    return msgpack.packb(obj)

def unpack_object(binary):
    return msgpack.unpackb(binary, encoding='utf-8')

def pack_io_object(obj, defs):
    """Pack an I/O object efficiently

    :param obj: object to pack
    :param defs: key definitions (input.json, etc.)
    :returns: interstitial representation of the object
    :raises KeyError: if the key is not in the key definitions
    """

    prepacked = {}
    for key in obj:
        if not key in defs:
            raise KeyError('key \'{}\' not in defs!'.format(key))

        if defs[key]['type'] == 'csv':
            # create a string object to write to
            out = io.StringIO()
            writer = csv.writer(out)
            writer.writerows(obj[key])
            prepacked[key] = out.getvalue()
        elif defs[key]['type'] == 'binary':
            # store binary as hex
            prepacked[key] = binascii.hexlify(obj['key'])
        else:
            # text/json need no processing
            prepacked[key] = obj[key]

    return prepacked

def unpack_io_object(obj, defs):
    """Unpack an I/O object efficiently

    :param obj: interstitial to unpack
    :param defs: key definitions (input.json, etc.)
    :returns: unpacked I/O object
    :raises KeyError: if the key is not in the key definitions
    """

    out = {}
    for key in obj:
        if not key in defs:
            raise KeyError('key \'{}\' not in defs!'.format(key))

        if defs[key]['type'] == 'csv':
            # create a string object to read from
            csv_f = io.StringIO(obj[key])
            reader = csv.reader(csv_f)
            out[key] = list(reader)
        elif defs[key]['type'] == 'binary':
            # store binary as hex
            out[key] = binascii.unhexlify(obj['key'])
        else:
            # text/json need no processing
            out[key] = obj[key]
    return out

