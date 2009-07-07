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
# Subclass of NSOutlineView, used to diplay layers in image
#

from PythonCAD.Interface.Cocoa import Globals
import PythonCAD.Generic.layer
from AppKit import NSOutlineView, NSMenu, NSMenuItem

class LayerOutlineView(NSOutlineView):
    """ Subclass of NSOutlineView, used to display layers
    
The purpose of the subclass is primarily to allow custom
context menus for the layer items. 

    """
    def menuForEvent_(self, event):
        _point = self.convertPoint_fromView_(event.locationInWindow(), None)
        _index = self.rowAtPoint_(_point)
        if -1 == _index:
            return None

        if not self.isRowSelected_(_index):
            self.selectRow_byExtendingSelection_(_index, False)

        _item = self.itemAtRow_(_index)
        _layer = Globals.unwrap(_item)
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        
        _menu = NSMenu.alloc().initWithTitle_("Context")
        _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Rename", "EditLayerName:", "")
        _menu.addItem_(_menuItem)
        if _layer.isVisible():
            _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide", "HideLayer:", "")
        else:
            _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show", "ShowLayer:", "")            
        _menuItem.setRepresentedObject_(_item)
        _menu.addItem_(_menuItem)
        _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Add Child Layer", "AddChildLayer:", "")
        _menuItem.setRepresentedObject_(_item)
        _menu.addItem_(_menuItem)
        _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Clear", "ClearLayer:", "")
        _menuItem.setRepresentedObject_(_item)
        _menu.addItem_(_menuItem)
        if _layer.hasChildren():
            _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Hide Children", "HideChildLayers:", "")
            _menuItem.setRepresentedObject_(_item)
            _menu.insertItem_atIndex_(_menuItem, 3)
            _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show Children", "ShowChildLayers:", "")
            _menuItem.setRepresentedObject_(_item)
            _menu.insertItem_atIndex_(_menuItem, 4)
        elif _layer.getParentLayer() is not None:
            _menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Delete", "DeleteLayer:", "")
            _menuItem.setRepresentedObject_(_item)
            _menu.addItem_(_menuItem)
        return _menu
            
        
        


        
            
            
