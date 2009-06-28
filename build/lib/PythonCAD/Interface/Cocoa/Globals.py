#
# Copyright (c) 2002-2004 Art Haas
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
# Global strings/utility classes stored here
#

from Foundation import NSObject

# Strings for Preferences
WinFrameName = "CADWindow"
LayerColumnName = "LayerName"
LayerAddedNotification = "PCAddLayer"
LayerDeletedNotification = "PCDelLayer"
ToolChangedNotification ="PCToolChanged"

# Class to keep weak referenced/non-retained objects
# from causing crashes.
WRAPPED ={}

class ObjWrap(NSObject):
    """This class is here to wrap python objects as objective-c objects
    
    """
    def init_(self, obj):
        self.obj = obj
        return self
    
def wrap(item):
    if WRAPPED.has_key(item):
        return WRAPPED[item]
    else:
        WRAPPED[item] = ObjWrap.alloc().init_(item)
        return WRAPPED[item]

def unwrap(item):
    if item is None:
        return item 
    return item.obj
    
def purge(item):
    if WRAPPED.has_key(item):
        del WRAPPED[item]
    
