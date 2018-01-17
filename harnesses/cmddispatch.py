#! /usr/bin/env python

import cmd
import sys
import json
import zmq
from termcolor import colored
from crux.common.messaging import Message, MessageException
from crux.common.logging import Logger


class CruxShell(cmd.Cmd):
    # zmq crap
    __context = None
    __socket = None
    __addr = None

    # message saving and stuff
    last_msg = None
    current_msg = None
    saved_msgs = {}

    # logging
    __log = None

    def __init__(self):
        super().__init__()

        self.__log = Logger(logging=True)
        # set up zmq stuff
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.REQ)

        self.current_msg = Message()
        self.__set_prompt()

    def __set_prompt(self):
        if self.__addr is None:
            state = colored('disconnected', 'red')
        else:
            state = colored(self.__addr, 'green')
        self.prompt = '({})> '.format(state)

    def exit(self):
        if self.__addr is not None:
            self.do_disconnect()

    def load(self, cmds):
        stripped = []
        for c in cmds:
            c = c.strip()
            if c != '':
                stripped.append(c)

        self.__log('preloading {}'.format(stripped))

        self.cmdqueue.extend(stripped)

    def message_show(self, msg):
        if msg is None:
            print(colored('no message', 'yellow'))
            return
        print('{}: {}'.format(
            colored('name', 'blue'),
            json.dumps(msg.name) if msg.name is not None else colored('None', 'red')
        ))
        print('{}: {}'.format(
            colored('payload', 'blue'),
            json.dumps(msg.payload) if msg.payload is not None else colored('None', 'red')
        ))
        print('{}: {}'.format(
            colored('success', 'blue'),
            json.dumps(msg.success) if msg.success is not None else colored('None', 'red')
        ))

    def do_EOF(self, arg):
        self.exit()
        print("")
        return True

    def do_exit(self, arg):
        self.exit()
        return True

    def do_connect(self, addr):
        if self.__addr is not None:
            self.__log.warn('socket was connected to {}, disconnecting...'
                            .format(self.__addr))
            self.__socket.disconnect(self.__addr)
        self.__addr = addr
        self.__socket.connect(self.__addr)
        self.__log.info('connected to {}'.format(self.__addr))
        self.__set_prompt()

    def do_disconnect(self):
        if self.__addr is not None:
            self.__socket.disconnect(self.__addr)
            self.__log.info('disconnected from {}'.format(self.__addr))
        else:
            self.__log.warn('socket was not connected, ignoring...')
        self.__addr = None
        self.__set_prompt()

    def do_cset(self, args):

        try:
            field, data = args.split(' ', 1)
        except:
            self.__log.error('error parsing arguments')
            return
        if not field in ['name', 'payload', 'success']:
            self.__log.error('invalid field \'{}\''.format(field))
            return
        try:
            setattr(self.current_msg, field, json.loads(data))
        except json.decoder.JSONDecodeError as jde:
            self.__log.error('invalid data \'{}\''.format(data))
        else:
            self.__log.info('set field {} to {}'.format(field, data))

    def do_cshow(self, _):
        self.message_show(self.current_msg)

    def do_creset(self, _):
        self.current_msg = Message()

    def do_lshow(self, _):
        self.message_show(self.last_msg)

    def do_lreset(self, _):
        self.last_msg = None

    def do_echo(self, txt):
        print('[{}]: {}'.format(colored('echo ', 'magenta'), txt))

    def do_send(self, _):
        if self.__addr is None:
            self.__log.error('not connected!')
            return
        try:
            packed = self.current_msg.pack()
        except MessageException as me:
            self.__log.error(me.msg)
        else:
            self.__socket.send(packed)
            self.last_msg = Message(data=self.__socket.recv())
            self.__log('sending...')

if __name__ == '__main__':
    sh = CruxShell()
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as cmds:
            sh.load(cmds.read().splitlines())
    sh.cmdloop()
