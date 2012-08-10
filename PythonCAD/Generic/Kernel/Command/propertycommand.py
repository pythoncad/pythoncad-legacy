#!/usr/bin/env python
#
# Copyright (c) 2011 Matteo Boscolo
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
# This module provide a class for the property command
#
import math

from Kernel.exception                  import *
from Kernel.Command.basecommand        import *

class PropertyCommand(BaseCommand):
    """
        this class represents the property command
    """
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        self.autorestart=False
        self.exception=[ExcMultiEntity,ExcDicTuple]
        self.defaultValue=[None]
        self.message=["Select Entities: ", 
                        "Give me the property name and value :('color','green') ", 
                        ]

    def changeProp(self, _id):    
        """
            change the property at the entity 
        """
        entity=self.document.getEntity(_id)
        style=entity.getInnerStyle()
        style.Derived()
        for stylePropName,stylePropValue in self.value[1].items():
            style.setStyleProp(stylePropName,stylePropValue)
        entity.style=self.document.saveEntity(style)   
        self.document.saveEntity(entity)

    def applyCommand(self):
        if len(self.value)!=2:
            raise PyCadWrongImputData("Wrong number of input parameter")
        try:
            self.document.startMassiveCreation()
            
            for _id in str(self.value[0]).split(','):
                self.changeProp(_id)
        except Exception,ex:
            raise ex
        finally:
            self.document.stopMassiveCreation()
