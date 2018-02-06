##
# crux cli harness
# @author Patrick Kage


import sys
import zmq
import json
import progressbar
from crux.backend.pool import ProcessPool
from crux.common.logging import Logger
from crux.backend.pipelineagent import PipelineAgent, BrokenPipelineError


def run_pipeline(descfile, daemon_addr=None):
    # create a logger
    log = Logger(logging=True, name='harness')

    # create the zmq context
    context = zmq.Context()

    # loading the agent
    if daemon_addr is None:
        pp = ProcessPool(use_ipc=True)
        log.info('using a process pool with IPC transport')
        agent = PipelineAgent(context=context, pool=pp)
    else:
        log.info('using a daemon located at {}'.format(daemon_addr))
        agent = PipelineAgent(context=context, daemon_addr=daemon_addr)

    # load descriptor
    with open(descfile, 'r') as handle:
        desc = json.load(handle)
        log('loaded description {}'.format(descfile))

    # progress bar widgets
    widgets = [progressbar.Percentage(), progressbar.Bar()]
    with progressbar.ProgressBar(widgets=widgets, max_value=len(desc['pipeline']), redirect_stdout=True) as pbar:
        try:
            pbar.update(0)
            for count, step, result in agent.run(desc):
                log.debug('exec {} {}'.format(
                    step['component'],
                    ('(' + str(len(result.payload['text'])) + ' bytes)') if result.payload is not None and 'text' in result.payload else ''
                ))
                pbar.update(count)
        except BrokenPipelineError as bpe:
            log.error('pipeline broke! {}'.format(bpe.msg))

    log.info('execution finished!')

    if daemon_addr is None:
        log.info('releasing process pool')
        pp.terminate_all()


