#! /usr/bin/env python

from crux.pipeline.component import Component
from crux.common.messaging import Message

# create the component against a hard-coded running instance
component = Component('tcp://127.0.0.1:30020')
print('doing request')
result = component.request(Message(
    name='execute',
    payload={
        'inputs': 'foo',
        'parameters': {}
    }
))

print(result)

