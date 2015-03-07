#!/usr/bin/python
import sys
import unittest
v = 1
if len(sys.argv) == 2: v = int(sys.argv[1])
suite = unittest.TestLoader().discover("test", "*_spec.py")
unittest.TextTestRunner(verbosity = v).run(suite)
