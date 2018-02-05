##
# crux client wizards
# @author Patrick Kage

import sys
import zmq
import click

from crux.backend.daemon_api import DaemonAPI

from . import initializer
from . import repl

@click.group()
def launch():
    """Crux command line configuration tool"""
    pass

@launch.command()
@click.option('--path', default='.', help='directory to initialize into')
@click.option('--name', prompt='Component name', help='component name')
@click.option('--author', metavar='name', help='The author to use, otherwise set from $USER')
def init(path, name, author):
    """intialize a crux client component"""
    initializer.create(name, path=path, author=author)
    click.echo('initialized component {} at {}'.format(
        name,
        path
    ))

@launch.command('repl')
@click.option('--script', help='script to execute', metavar='file')
def start_repl(script):
    """A low-level debugging REPL"""
    repl.start(script)

@launch.group()
@click.option('--uri', default='tcp://127.0.0.1:30020', metavar='URI', help='uri of the daemon to connect to')
@click.pass_context
def daemon(ctx, uri):
    """Communicate with the daemon"""
    ctx.obj = {'URI': uri, 'ctx': zmq.Context()}
    pass

@daemon.command('process_list')
@click.pass_context
def daemon_proclist(ctx):
    """List the addresses of the processes managed by the daemon."""
    for proc in DaemonAPI(ctx.obj['URI'], context=ctx.obj['ctx']).process_list().payload:
        click.echo(proc)

@daemon.command('process_start')
@click.argument('path')
@click.pass_context
def daemon_procstart(ctx, path):
    """Start a process managed by the daemon"""
    click.echo(DaemonAPI(ctx.obj['URI'], context=ctx.obj['ctx']).process_start(path).payload)

@daemon.command('process_killall')
@click.pass_context
def daemon_prockillall(ctx):
    """Kill all the processes managed by the daemon"""
    DaemonAPI(ctx.obj['URI'], context=ctx.obj['ctx']).process_killall()
    click.echo('Command issued.')

@daemon.command('shutdown')
@click.pass_context
def daemon_shutdown(ctx):
    """Shut down the daemon"""
    DaemonAPI(ctx.obj['URI'], context=ctx.obj['ctx']).shutdown()
    click.echo('Command issued.')


@launch.command()
@click.option('--port', default='8080', help='port to serve on')
def web(port):
    """start the web interface"""
    click.echo('not yet implemented!')
