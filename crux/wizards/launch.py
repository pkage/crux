##
# crux client wizards
# @author Patrick Kage

import sys
import click

from . import initializer

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
