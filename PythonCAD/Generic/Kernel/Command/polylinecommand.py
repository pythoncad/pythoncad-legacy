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
# You should have received a copy of the GNU General Public Licensesegmentcmd.py
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#This module provide a class for the polyline command
#

from Generic.Kernel.exception               import *
from Generic.Kernel.Command.basecommand     import *
from Generic.Kernel.Entity.polyline         import Polyline

class PolylineCommand(BaseCommand):
    """
        this class rappresent the ellips command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcPoint]
        self.message=["Give Me A Point"]
        self.raiseStop=False
    def next(self):
        """
            performe iteration
            overwrite the default next into an infinite loop
            we do not know how mani points the user whant to insert
        """
        if self.raiseStop:
            raise StopIteration
        return (self.exception[0],self.message[0])
    def __setitem__(self, key, value):
        """
            overwrite the command to perform the stop operation
        """
        if value:
            self.value.append(value)    
        else:
           self.raiseStop=True 
    def applyCommand(self):
        """
            perform the write of the entity
        """
        pline=Polyline(self.value)
        self.document.saveEntity(pline)
