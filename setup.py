#!/usr/bin/env python
#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
#

#
# Install pythoncad using the distutils method
#

from distutils.core import setup

setup(name="PythonCAD",
      version="DS1-R36",
      description="CAD built from Python",
      author="Art Haas",
      author_email="ahaas@airmail.net",
      url="http://www.pythoncad.org/",
      license="GPL",
      packages=['PythonCAD',
                'PythonCAD/Generic',
                'PythonCAD/Interface',
                'PythonCAD/Interface/Cocoa',
                'PythonCAD/Interface/Gtk'],
     )
