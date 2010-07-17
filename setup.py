#!/usr/bin/env python
#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo

#
# Install pythoncad using the distutils method
#

from distutils.core import setup

setup(name="PythonCAD",
      version="DS1-R38-Alfa",
      description="CAD built from Python",
      author="Art Haas, Matteo Boscolo",
      author_email="ahaas@airmail.net,matteo.boscolo@boscolini.eu",
      url="http://sourceforge.net/projects/pythoncad",
      license="GPL",
      packages=['PythonCAD',
                'PythonCAD/Generic',
                'PythonCAD/Generic/Kernel',
                'PythonCAD/Interface',],
     )
