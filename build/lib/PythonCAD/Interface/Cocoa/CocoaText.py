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
# Handles creation of text entries
#

import objc

import PythonCAD.Generic.tools
import PythonCAD.Generic.text

import CocoaEntities
from AppKit import NSFontManager, NSItalicFontMask, NSTextView

def textview_format_setup(doc, textview):
    textview.setString_("")
    _family = doc.getOption('FONT_FAMILY')
    _weight = doc.getOption('FONT_WEIGHT')
    _style = doc.getOption('FONT_STYLE')
    _size = doc.getOption('FONT_SIZE')
    _color = doc.getOption('FONT_COLOR')
    _fm = NSFontManager.sharedFontManager()
    _traits = 0
    if PythonCAD.Generic.text.TextStyle.FONT_ITALIC == _style:
        _traits = _traits | NSItalicFontMask
    if PythonCAD.Generic.text.TextStyle.WEIGHT_LIGHT == _weight:
        _weight = 3
    if PythonCAD.Generic.text.TextStyle.WEIGHT_NORMAL == _weight:
        _weight = 5
    elif PythonCAD.Generic.text.TextStyle.WEIGHT_BOLD == _weight:
        _weight = 9
    elif PythonCAD.Generic.text.TextStyle.WEIGHT_HEAVY == _weight:
        _weight = 11
    _font = _fm.fontWithFamily_traits_weight_size_(_family, _traits, _weight, _size)
    if _font is None:
        return
    textview.setFont_(_font)
        
def text_entered(doc, tool, textview):
    doc.setPrompt("Click where to place the text.")
    tool.setHandler("mouse_move", text_mouse_move_cb)
    tool.setHandler("left_button_press", text_left_button_press_cb)
    
def text_mouse_move_cb(doc, np, tool):
    (_x, _y) = np
    _text = tool.getText()
    _style = doc.getOption('TEXT_STYLE')
    _tblock = PythonCAD.Generic.text.TextBlock(_text, _style)
    _tblock.setLocation(_x, _y)
    _da = doc.getDA()
    _da.setTempObject(_tblock)
    
def text_left_button_press_cb(doc, event, tool):
    _loc = event.locationInWindow()
    _da = doc.getDA()
    _viewLoc = _da.convertPoint_fromView_(_loc, None)
    tool.setTextLocation(_viewLoc.x, _viewLoc.y)
    tool.create(doc.getImage())
    tool.reset()
    doc.setPrompt("Enter command:")
    

    
