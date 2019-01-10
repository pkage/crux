##
# Launch information for crux
# @author Patrick Kage

import click
from . import daemon

# entry point for console script
@click.command()
@click.option('--debug', default=False, help='Enable debug mode', is_flag=True)
@click.option('--logging/--silent', default=True, help='Enable/disable logging')
@click.option('--bind-addr', metavar='URI', default='tcp://*:30020', help='Bind URI for the daemon')
@click.option('--pub-addr', metavar='URI', default='tcp://*:30021', help='Pub URI for the daemon vent')
@click.option('--install-location', metavar='PATH', default='/opt/crux', help='Installation location for crux components')
def main(debug, logging, bind_addr, pub_addr, install_location):
    """Launcher for the crux daemon"""

    # initialize the daemon
    cruxd = daemon.Daemon(
        logging=logging,
        debug=debug,
        bind_addr=bind_addr,
        pub_addr=pub_addr,
        install_loc=install_location
    )

    # guarded here to make sure we flush the pool
    with cruxd:
        cruxd.listen()
