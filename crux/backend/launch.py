##
# Launch information for crux
# @author Patrick Kage

import argparse
from . import daemon

# entry point for console script
def main():
    ap = argparse.ArgumentParser(description='crux daemon launch agent')

    ap.add_argument('-b', '--bind-addr', default='tcp://*:30020',
                    help='URI for the daemon to bind the API against')
    ap.add_argument('-p', '--pub-addr', default='tcp://*:30021',
                    help='URI for the daemon to bind the notification server against')

    ap.add_argument('--debug', help='enable debug mode', action='store_true')
    ap.add_argument('--logging', help='enable logging', action='store_true')

    args = ap.parse_args()

    # initialize the daemon
    cruxd = daemon.Daemon(
        logging=args.logging,
        debug=args.debug,
        bind_addr=args.bind_addr,
        pub_addr=args.pub_addr
    )

    # launch the daemon
    cruxd.listen()
