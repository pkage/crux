#! /usr/bin/env python

import zmq
from crux.backend.pool import ProcessPool
from crux.pipeline.component import Component
from crux.common.messaging import Message

context = zmq.Context()
pool = ProcessPool()

address = pool.launch('../examples/client/')
component = Component(address, context=context)

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

