#! /usr/bin/env python

import zmq
from crux.backend.pool import ComponentPool
from crux.common.messaging import Message

context = zmq.Context()
pool = ComponentPool()

component = pool.launch('../examples/client/', context=context)

print('doing request')
result = component.request(Message(
    name='execute',
    payload={
        'inputs': 'foo',
        'parameters': {}
    }
))
print(result)

pool.join_all()

