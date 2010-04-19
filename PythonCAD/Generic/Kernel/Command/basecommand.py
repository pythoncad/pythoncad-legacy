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
#This module provide basic command function
#
from Generic.Kernel.exception           import *

class BaseCommand(object):
    """
        this class provide a base command
    """
    def __init__(self, document):
        """
            kernel is a PyCadKernel object
        """
        self.exception=[]
        self.value=[]
        self.message=[]
        self.index=-1
        self.document=document
    def __iter__(self):
        return self
    def next(self):
        """
            performe iteration
        """
        self.index+=1
        TotNIter=len(self.exception)
        if self.index>=TotNIter:
            raise StopIteration
        return (self.exception[self.index],self.message[self.index])

    def __setitem__(self, key, value):
        """
            set the value of the command
        """
        self.value.append(value)
        
    def applyCommand(self):
        """
            this method here must be defined
        """
        pass
