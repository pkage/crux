##
# crux client wizards
# @author Patrick Kage

import sys
import click

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

