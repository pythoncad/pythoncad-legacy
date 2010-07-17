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
        self.defaultValue=[]
        self.index=-1
        self.document=document
    
    def resetToDefault(self):    
        self.value=[]
        for val in self.defaultValue:
            self.value.append(val)

    def __iter__(self):
        return self
        
    def reset(self):
        self.index=-1
        self.value=[]
    @property
    def valueIndex(self):    
        """
            get the index of the insert value in the command
        """
        return len(self.value)
    def next(self):
        """
            go on with the iteration
        """
        self.index+=1
        TotNIter=len(self.exception)
        if self.index>=TotNIter:
            raise StopIteration
        return (self.exception[self.index],self.message[self.index])
    
    def activeException(self):
        """
            Return the active exception
        """
        return self.exception[self.index]
        
    def activeMessage(self):
        """
            return the active Message
        """
        return self.message[self.index]
    
    def activeDefaultValue(self):
        """
            Return the active default value
        """
        return self.defaultValue[self.index]
        
    def previus(selfself):
        """
            came back with the iteration
        """
        self.index-=1
        if self.index<=0:
            self.index=0
        return (self.exception[self.index],self.message[self.index])       
    
    def keys(self):
        """
            return all the exception key
        """
        return self.exception
        
    def __setitem__(self, key, value):
        """
            set the value of the command
        """
        self.value.append(value)
    
    @property
    def lenght(self):
        return len(self.exception)
    
    def applyCommand(self):
        """
            this method here must be defined
        """
        pass
        
    def getActiveDefaultValue(self):
        if self.index>=0 and self.index<=len(self.defaultValue)-1:
            return self.defaultValue[self.index]
        else:
            return None
            
    def getActiveMessage(self):
        """
            get Active message
        """
        _index=self.index+1
        if len(self.message)>_index:
            return self.message[_index]
        else:
            return "Press enter to ececute the command"
