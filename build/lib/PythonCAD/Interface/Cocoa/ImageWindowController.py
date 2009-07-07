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
# Cocoa CAD drawing window controller, delegate of split view
#
# P.L.V. nov 23 05
# import adjustment

import string
import PythonCAD.Generic.layer
import PythonCAD.Generic.keywords

import PythonCAD.Interface.Cocoa.CADView
import PythonCAD.Interface.Cocoa.LayerView
import PythonCAD.Interface.Cocoa.CocoaPrompt
import PythonCAD.Interface.Cocoa.Globals
import PythonCAD.Interface.Cocoa.AppController
from PythonCAD.Interface.Cocoa.Globals import WinFrameName, LayerDeletedNotification, LayerAddedNotification, ToolChangedNotification

from PyObjCTools import NibClassBuilder
from AppKit import *
from Foundation import NSNotificationCenter

#
# Define True & False in case this is Python < 2.2.1
#
try:
    True, False
except NameError:
    True, False = 1, 0

    
class ImageWindowController(NSWindowController, NSOutlineViewDataSource):
    """ Custom NSWindowController for ImageDocument window
    
An ImageWindowController is a NSWindowController used to manage
the NSWindow used by the ImageDocument class.  It is the delegate
of the NSSplitView & NSOutlineView (holding the layers), & NSWindow
    """
#
# Beginning of Cocoa methods
#

    def initWithWindowNibName_owner_(self, nib, owner):
        self = super(ImageWindowController, self).initWithWindowNibName_owner_(nib, owner)
        if (self):
            self.__outlineView = None
            self.__splitView = None
        return self
        
    def windowDidLoad(self):
        _doc = self.document()
        _sv = _doc.getSplitView()
        _ov = _doc.getOutlineView()
        _text = _doc.getEntry()
        _win = self.window()
        _text.setDelegate_(self)
        _sv.setDelegate_(self)
        _win.setDelegate_(self)
        _win.setFrameUsingName_(WinFrameName)
        _ov.setDataSource_(self)
        _ov.setDelegate_(self)
        _ov.sizeLastColumnToFit()
        _ov.setAutoresizesOutlineColumn_(True)
        _da = _doc.getDA()
        _scrv = _da.enclosingScrollView()
        _scrvSize = _scrv.contentSize()
        _scrv.setCopiesOnScroll_(False)
        _da.setFrameSize_(_scrvSize)
        #
        # ensure selected layer is active
        #
        _item = _ov.itemAtRow_(0)
        _ov.expandItem_expandChildren_(_item, True)
        _endRow = _ov.numberOfRows() - 1
        _ov.selectRow_byExtendingSelection_(_endRow, False)
        _ov.selectRow_byExtendingSelection_(0, False)
        #
        # Register for notifications of changes to the document
        #
        _img = _doc.getImage()
        _obj = Globals.wrap(_img)
        _nc = NSNotificationCenter.defaultCenter()
        _nc.addObserver_selector_name_object_(self, "layerChanged:", LayerAddedNotification, _obj)
        _nc.addObserver_selector_name_object_(self, "layerChanged:", LayerDeletedNotification, _obj)
        _nc.addObserver_selector_name_object_(self, "toolChanged:", ToolChangedNotification, _doc)
        
    def windowDidResize_(self, note):
        _win = note.object()
        _win.saveFrameUsingName_(WinFrameName)
        
    def windowWillClose_(self, note):
        _nc = NSNotificationCenter.defaultCenter()
        _nc.removeObserver_(self)
        
        
#
# Beginning of Split View delegate methods
#

    def splitView_resizeSubviewsWithOldSize_(self, splitView, oldSize):
        """Resize split view subviews after size change to oldSize

splitView_resizeSubviewsWithOldSize_(self, splitView, oldSize)
        """
        _ov = self.document().getOutlineView()
        _cadView = self.document().getDA()
        _subviewArray = splitView.subviews()

        for _count in range(_subviewArray.count()):
            _aView = _subviewArray.objectAtIndex_(_count)
            if (_ov.isDescendantOf_(_aView)):
                _ov = _aView
            elif (_cadView.isDescendantOf_(_aView)):
                _cadView = _aView
                    
        _ovFrame = _ov.frame()
        _cadFrame = _cadView.frame()
        _splitSize = splitView.frame().size
        _extraWidth = splitView.dividerThickness() + _ovFrame.size.width
        _ovFrame.size.height = _splitSize.height
        _cadFrame.size.height = _splitSize.height
        if _extraWidth < _splitSize.width:
            _cadFrame.size.width = _splitSize.width - _extraWidth 
        else:
            splitView.adjustSubviews()
        _ov.setFrame_(_ovFrame)
        _cadView.setFrame_(_cadFrame)
                
#
# End of Split View delegate methods
#

#
# Beginning of Outline View delegate methods
#
    def outlineViewSelectionDidChange_(self, note):
        _ov = note.object()
        _index = _ov.selectedRow()
        if -1 != _index:
            _item = _ov.itemAtRow_(_index)
            _layer = Globals.unwrap(_item)
            _doc = self.document()
            _doc.getImage().setActiveLayer(_layer)
            _doc.getDA().setNeedsDisplay_(True)
    
    def outlineViewItemDidCollapse_(self, note):
        _doc = self.document()
        _active_layer = _doc.getImage().getActiveLayer()
        _ov = note.object()
        _row = _ov.rowForItem_(Globals.wrap(_active_layer))
        if -1 == _row:
            _item = note.userInfo()["NSObject"]
            _row = _ov.rowForItem_(_item)
            _ov.selectRow_byExtendingSelection_(_row, False)
    
    def outlineView_willDisplayCell_forTableColumn_item_(self, ov, cell, tc, item):
        _layer = Globals.unwrap(item)
        if _layer.isVisible():
            _color = NSColor.blackColor()
        else:
            _color = NSColor.lightGrayColor()
        cell.setTextColor_(_color)  
        
#
# Outline view data source methods
#
#
# Beginning of OutlineView Data source methods
#
    def outlineView_isItemExpandable_(self, outlineView, item):
        """ NSOutlineViewDataSource method for layer view 

outlineView_isItemExpandable_(outlineView, item)
        """
        _item = Globals.unwrap(item)
        if _item is None:
            return True # Top Layer item is always displayed
        return _item.hasSublayers()
    
    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        """ NSOutlineViewDataSource method for layer view 

outlineView_numberOfChildrenOfItem_(outlineView, item)
        """
        _item = Globals.unwrap(item)
        if _item is None:
            return 1 # Top Layer item is first item in layer list
        return len(_item.getSublayers())
        
    def outlineView_child_ofItem_(self, outlineView, itemIndex, item):
        """ NSOutlineViewDataSource method for layer view 

outlineView_child_ofItem_(outlineView, itemIndex, item)
        """
        _item = Globals.unwrap(item)
        if _item is None:
            return Globals.wrap(self.document().getImage().getTopLayer())
        _children = _item.getSublayers()
        return Globals.wrap(_children[itemIndex])
        
    def outlineView_objectValueForTableColumn_byItem_(self, ov, tc, item):
        """ NSOutlineViewDataSource method for layer view 

outlineView_objectValueForTableColumn_byItem_(outlineView, tableColumn, item)
        """
        if tc.identifier() != Globals.LayerColumnName:
            return None
        _item = Globals.unwrap(item)
        if _item is None:
            _item = self.document().getImage().getTopLayer()
        return _item.getName()
        
    def outlineView_setObjectValue_forTableColumn_byItem_(self, ov, val, tc, item):
        """ NSOutlineViewDataSource method for layer view
        
outlineView_setObjectValue_forTableColumn_byItem_(outlineView, value, tableColumn, item)
        """
        if tc.identifier() != Globals.LayerColumnName:
            return
        _layer = Globals.unwrap(item)
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid active Layer: " + `_layer`
        _layer.setName(val)


    def layerChanged_(self, note):
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        _dict = note.userInfo()
        _parent = Globals.wrap(_dict["parent"])
        _ov = _doc.getOutlineView()
        _image = _doc.getImage()
        _l = _activeLayer = _image.getActiveLayer()
#        _ov.reloadItem_reloadChildren_(_parent, True)
        _ov.reloadData()
        _topLayer = _image.getTopLayer()
        _stack = []
        while _l is not _topLayer:
            _l = _l.getParentLayer()
            _stack.append(_l)
        while len(_stack):
            _item = Globals.wrap(_stack.pop())
            _ov.expandItem_(_item)
        _al = Globals.wrap(_activeLayer)
        _row = _ov.rowForItem_(_al)
        _ov.selectRow_byExtendingSelection_(_row, False)
        
    def toolChanged_(self, note):
        _sheet = self.window().attachedSheet()
        if _sheet is None:
            return
        _userinfo = note.userInfo()
        _tool = _userinfo["tool"]
        if not isinstance(_tool, PythonCAD.Generic.tools.TextTool):
            NSApplication.sharedApplication().endSheet_(_sheet)
            _sheet.orderOut_(_sheet)
            
        
               
#
# Layer context menu functions
#    
    def EditLayerName_(self, sender):
        _ov = self.document().getOutlineView()
        _row = _ov.selectedRow()
        _ov.editColumn_row_withEvent_select_(0, _row, None, True)
        
    def HideLayer_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _layer.hide()
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        _doc.getOutlineView().setNeedsDisplay_(True)

    def ShowLayer_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _layer.show()
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        _doc.getOutlineView().setNeedsDisplay_(True)
                
    def AddChildLayer_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _doc = self.document()
        _doc.addChildLayer(_layer)
        
    def HideChildLayers_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _children = _layer.getSublayers()
        while(len(_children)):
            _child = _children.pop()
            _child.hide()
            if _child.hasSublayers():
                _children = _children + _child.getSublayers()
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        _doc.getOutlineView().setNeedsDisplay_(True)
        
    def ShowChildLayers_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _children = _layer.getSublayers()
        while(len(_children)):
            _child = _children.pop()
            _child.show()
            if _child.hasSublayers():
                _children = _children + _child.getSublayers()
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        _doc.getOutlineView().setNeedsDisplay_(True)
        
    def ClearLayer_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _layer.clear()
        _doc = self.document()
        _doc.getDA().setNeedsDisplay_(True)
        
    def DeleteLayer_(self, sender):
        _layer = Globals.unwrap(sender.representedObject())
        if not isinstance(_layer, PythonCAD.Generic.layer.Layer):
            raise TypeError, "Invalid Layer: " + `_layer`
        _doc = self.document()
        _doc.delLayer(_layer)

#
# End of Layer context menu functions       
#
       
#
#   somebody entered something in the entry event
#
    def controlTextDidEndEditing_(self, note):
        _doc = self.document()
        _tool = _doc.getTool()
        _field = note.object()
        _text = string.strip(string.lower(_field.stringValue()))
        _cmds = PythonCAD.Generic.keywords.defaultglobals
        if _text == 'end' or _text == 'stop':
            _doc.reset()
        elif _text in _cmds:
                _opt = _cmds[_text]
                _cmd = CocoaPrompt.lookup(_opt)
                NSApp = NSApplication.sharedApplication()
                try:
                    eval(_cmd)
                except:
                    NSBeep()
        elif _tool is not None and _tool.hasHandler("entry_event"):
            _handler = _tool.getHandler("entry_event")
            try: 
                _handler(_doc, _text, _tool)
            except:
                NSBeep()

    

#
# Beginning of NSWindow delegate methods
#
#    def windowWillResize_toSize_(self, win, size):
#        if not self.__inResize:
#            self.__inResize = True
#            _da = self.document().getDA()
#            _img = _da.getImageRep()
#            _iv = NSImageView.alloc().initWithFrame_(_da.frame())
#            _iv.setImage_(_img)
#            self.__dasv = _da.enclosingScrollView() 
#            _da.removeFromSuperviewWithoutNeedingDisplay()
#            self.__dasv.setDocumentView_(_iv)
#        return size
        
        
        
#
# End of NSWindow Delegate methods
#

#
# End of Cocoa methods
#

    
