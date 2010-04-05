#!/usr/bin/env python
#
# Copyright (c) 2010 Matteo Boscolo
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PythonCAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# This  module provide the main api interface of pythoncad
#
#
import sys
from Generic.Kernel.pycaddbexception    import *
from Generic.Kernel.pycadkernel         import *
from Generic.Kernel.pycadcommands       import *
from Generic.Kernel.Entity.point        import Point


class PyCadApplication(object):
    """
        this class provide the real pythoncad api interface ..
    """
    def __init__(self):
        self.kernel=PyCadDbKernel()
        self.__applicationCommand=APPLICATION_COMMAND


    def getCommand(self,commandType):
        """
            Get a command of commandType
        """
        if self.__applicationCommand.has_key(commandType):
            cmd=self.__applicationCommand[commandType]
            cmdIstance=cmd(self.kernel) #fixme : c'e' un errore qui ... controllare
            return cmdIstance
        else:
            raise PyCadWrongCommand("")




