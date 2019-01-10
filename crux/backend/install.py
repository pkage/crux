##
# Crux component installation
# @author Patrick Kage

import os
import unzip
from git import Repo
from crux.common.logging import Logger

def install_repo(self, url, dest):
    Repo.clone_from(url, dest)

