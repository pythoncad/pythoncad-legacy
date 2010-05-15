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
#This module provide a class for the champfer command
#
from Generic.Kernel.exception               import *
from Generic.Kernel.Command.basecommand     import *
from Generic.Kernel.Entity.segjoint         import Chamfer

class ChamferCommand(BaseCommand):
    """
        this class rappresent the champfer command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.exception=[ExcEntity,
                        ExcEntity, 
                        ExcLenght, 
                        ExcLenght, 
                        ExcPoint, 
                        ExcPoint ]
        self.message=["Give Me the first Entity", 
                        "Give Me the second entity", 
                        "Give Me the first Lenght", 
                        "Give Me the seconf Lenght", 
                        "Give me the first point near the first entity",
                        "Give me the second point near the second entity"]
    def applyCommand(self):
        """
            apply the champfer command
        """
        if len(self.value)!=6:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        cmf=Chamfer(self.value[0],
                    self.value[1], 
                    self.value[2], 
                    self.value[3], 
                    self.value[4], 
                    self.value[5])
        self.document.saveEntity(cmf)
