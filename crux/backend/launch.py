##
# Launch information for crux
# @author Patrick Kage

import argparse
from . import daemon

# entry point for console script
def main():
    ap = argparse.ArgumentParser(description='crux daemon launch agent')

    ap.add_argument('-b', '--bind-addr', required=True,
                    help='URI for the daemon to bind the API against')
    ap.add_argument('-p', '--pub-addr', required=True,
                    help='URI for the daemon to bind the notification server against')

    ap.add_argument('--debug', help='enable debug mode', action='store_true')
    ap.add_argument('--logging', help='enable logging', action='store_true')

    args = ap.parse_args()

    # initialize the daemon
    cruxd = daemon.Daemon(
        logging=args.logging,
        debug=args.debug
    )

    # launch the daemon
    cruxd.listen(
        args.bind_addr,
        args.pub_addr
    )
