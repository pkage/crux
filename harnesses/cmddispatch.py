#! /usr/bin/env python

import sys
from crux.wizards.repl import CruxREPL

repl = CruxREPL(sys.argv[1] if len(sys.argv) == 2 else None)
repl.cmdloop()
