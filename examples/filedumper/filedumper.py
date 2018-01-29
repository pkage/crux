#! /usr/bin/env python

##
# crux file dumper component
# @author Patrick Kage
# 
# this is an example (but still functional!) file dumper

import os
import json
from crux.client import CruxClient as Crux


def dump_file(cfg, content):
    print(cfg)
    with open(cfg['path'], 'w') as handle:
        data = handle.write(content)

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
            output = dump_file(config, data['content'])

            # output that data back to the backend
            cc.output(output)
        except Exception as e:
            # hard failure
            cc.fail()
    # do cleanup here if necessary
