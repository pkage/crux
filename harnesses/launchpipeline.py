#! /usr/bin/env python

import sys
import zmq
import json
from crux.backend.pool import ProcessPool
from crux.common.logging import Logger
from crux.backend.pipelineagent import PipelineAgent, BrokenPipelineError

# logger
log = Logger(logging=True, name='harness')

# zmq context
context = zmq.Context()
log('created zmq context')

# create pool
pp = ProcessPool(use_ipc=False)

# load descriptor
with open(sys.argv[1], 'r') as handle:
    desc = json.load(handle)

# create the execution agent
agent = PipelineAgent(context=context, pool=pp)

# iterate through all the steps
try:
    for count, step, result in agent.run(desc):
        log.info('executed step {}/{}'.format(
            count + 1,
            len(desc['pipeline'])
        ))
        log.debug('{}/{} {}'.format(
            step['component'],
            count,
            str(len(result.payload['text'])) + ' bytes' if result.payload is not None and 'text' in result.payload else ''
        ))
except BrokenPipelineError as bpe:
    log.error('pipeline broke! {}'.format(bpe.msg))

# clean up pool
log.info('cleaning up pool...')
pp.terminate_all()

# done!
log.info('exec done!')
