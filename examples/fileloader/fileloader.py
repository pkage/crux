#! /usr/bin/env python

##
# crux file loader component
# @author Patrick Kage
# 
# this is an example (but still functional!) file loader

import os
import json
from crux.client import CruxClient as Crux


def load_file(cfg):
    with open(cfg['path'], 'r') as handle:
        data = handle.read()

    if cfg['export'] == 'json':
        return {'json': json.loads(data)}
    elif cfg['export'] == 'csv':
        raise NotImplementedError()
    elif cfg['export'] == 'binary':
        return {'binary': data}
    else:
        return {'text': data}

if __name__ == "__main__":
    # initialize everything
    cc = Crux('crux.json')

    while True:
        # wait for the backend to send some data for processing
        data, config, done = cc.wait()

        if done:
            break

        try:
            # load the file
            output = load_file(config)

            # output that data back to the backend
            cc.output(output)
        except Exception as e:
            # hard failure
            cc.fail()
    # do cleanup here if necessary
