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
# This  module Provide custom exception for the db module and kernel
#

class StructuralError(Exception):
    """
        Very bad error that menans that the kernel has made somthing very bad 
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EmptyFile(Exception):
    """
        class for managin empty file 
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class StyleUndefinedAttribute(Exception):
    """
        Class for managing styleAttribute problems 
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

class PythopnCadWarning(Exception):
    """
        Class for raise a warning exception
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  
class EmptyDbSelect(Exception):
    """
        This exception is used for null return of
        db select
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EntityMissing(Exception):
    """
        This exception is used for null return of
        entity search
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    
    
class UndoDb(Exception):
    """
        This exception is used UndoDb class to manage is errors
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class EntDb(Exception):
    """
        Generic error on entity db creatioin
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DxfReport(Exception):
    """
        error to say that the report of dxf is ready to be visualized
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DxfUnsupportedFormat(Exception):
    """
        Unsupported format 
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#********************************
#       command exception
#********************************
class PyCadWrongCommand(Exception):
    """
        Wrong command for the PyCadApplication
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 

class PyCadWrongImputData(Exception):
    """
        Wrong command for the PyCadApplication
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 
#********************************
#       imput exception
#********************************
class ExcPoint(Exception):
    """
        when this exception is trown it means that the command need a point
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class ExcLenght(Exception):
    """
        when this exception is trown it means that the command need a lenght
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ExcAngle(Exception):
    """
        when this exception is trown it means that the command need a deg angle
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ExText(Exception):
    """
        when this exception is trown it means that the command need text
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
