#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo
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
# <> command functions/Class 
#

import pygtk
pygtk.require('2.0')
import gtk
import pango
import copy

from math import hypot, pi, atan2

from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import snap
from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import snap 
from PythonCAD.Interface.Command import cmdCommon
from PythonCAD.Generic import util
#
# Init
#
def text_add_init(gtkimage, tool=None):
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    if tool is not None:
        _image.setTool(tool)
    _tool = _image.getTool()
    _text = _tool.getText()
    _ts = _image.getOption('TEXT_STYLE')
    _tb = TextBlock(_x, _y, _text, _ts)
    _f = _image.getOption('FONT_FAMILY')
    if _f != _ts.getFamily():
        _tb.setFamily(_f)
    _s = _image.getOption('FONT_STYLE')
    if _s != _ts.getStyle():
        _tb.setStyle(_s)
    _w = _image.getOption('FONT_WEIGHT')
    if _w != _ts.getWeight():
        _tb.setWeight(_w)
    _c = _image.getOption('FONT_COLOR')
    if _c != _ts.getColor():
        _tb.setColor(_c)
    _sz = _image.getOption('TEXT_SIZE')
    if abs(_sz - _ts.getSize()) > 1e-10:
        _tb.setSize(_sz)
    _a = _image.getOption('TEXT_ANGLE')
    if abs(_a - _ts.getAngle()) > 1e-10:
        _tb.setAngle(_a)
    _al = _image.getOption('TEXT_ALIGNMENT')
    if _al != _ts.getAlignment():
        _tb.setAlignment(_al)
    _tool.setTextBlock(_tb)
    _layout = _make_pango_layout(gtkimage, _text, _f, _s, _w, _sz)
    _tool.setLayout(_layout)
    _lw, _lh = _layout.get_pixel_size()
    _tool.setPixelSize(_lw, _lh)
    _upp = gtkimage.getUnitsPerPixel()
    #
    # the width and height calculations can be somewhat inaccurate
    # as the unitsPerPixel value gets large
    #
    _w = _lw * _upp
    _h = _lh * _upp
    _tool.setBounds(_w, _h)
    _tool.setHandler("motion_notify", text_motion_notify)
    _tool.setHandler("button_press", text_button_press)
    gtkimage.setPrompt(_('Click where to place the text'))
    _gc = gtkimage.getGC()
    _gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                            gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
    _gc.set_function(gtk.gdk.INVERT)
#
# Motion Notifie
#
def text_motion_notify(gtkimage, widget, event, tool):
    _tblock = tool.getTextBlock()
    _tw, _th = tool.getPixelSize()
    _gc = gtkimage.getGC()
    _align = _tblock.getAlignment()
    if _align == TextStyle.ALIGN_LEFT:    
        _xoff = 0
    elif _align == TextStyle.ALIGN_CENTER:
        _xoff = _tw//2
    elif _align == TextStyle.ALIGN_RIGHT:
        _xoff = _tw
    else:
        raise ValueError, "Unexpected alignment value: %d" % _align
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _xc = _xc - _xoff
        widget.window.draw_rectangle(_gc, False, _xc, _yc, _tw, _th)
    _snapArray={'perpendicular':False,'tangent':False}
    _sn=snap.getSnapPoint(gtkimage.getImage(),gtkimage.getTolerance(),_snapArray)
    _x, _y=_sn.point.getCoords()
    _x = _x - _xoff    
    _x,_y = gtkimage.coordToPixTransform(_x,_y)
    tool.setCurrentPoint(_x,_y)
    widget.window.draw_rectangle(_gc, False, _x, _y, _tw, _th)
    return True
#
# Button press callBacks
#
def text_button_press(gtkimage, widget, event, tool):
    _image=gtkimage.getImage()
    _snapArray={'perpendicular':False,'tangent':False}
    _sn=snap.getSnapPoint(_image,gtkimage.getTolerance(),_snapArray)
    _x,_y=_sn.point.getCoords()    
    tool.getTextBlock().setLocation(_x,_y)
    _tool=copy.copy(tool)
    _image.startAction()    
    try:
        tool.create(_image)
    finally:
        _image.endAction()
    text_add_init(gtkimage,_tool)
    return True
#
# Entry callBacks
#

#
# Suport functions
#

def set_textblock_bounds(gtkimage, tblock):
    # print "set_textblock_bounds() ..."
    _text = tblock.getText()
    if len(_text) == 0:
        tblock.setBounds(0, 0)
        tblock.setFontScale(1/float(pango.SCALE))
        return
    _family = tblock.getFamily()
    _style = tblock.getStyle()
    _weight = tblock.getWeight()
    _size = tblock.getSize()
    _da = gtkimage.getDA()
    _upp = gtkimage.getUnitsPerPixel()
    #
    # initial test layout ...
    #
    try:
        _text=util.to_unicode(_text)
    except:
        print "Debug: Unable to unicode %s"%str(_text)
        _text="Error on converting in unicode"
    _layout = _da.create_pango_layout(_text)
    _fd = pango.FontDescription()
    _fd.set_family(_family)
    _fd.set_style(_style)
    _fd.set_weight(_weight)
    #
    # use an 18-point font as first size guess
    #
    _fs = 18
    _fd.set_size(pango.SCALE * _fs)
    _layout.set_font_description(_fd)
    _nlines = _layout.get_line_count()
    #
    # the pixel height of the TextBlock
    #
    _th = _nlines * _size
    # print "TextBlock height: %g" % _th
    _ph = _th/_upp 
    _iph = int(_ph)
    if _iph/_nlines < 3: # tiny text - use the 18-point values for boundary
        _w, _h = _layout.get_size()
        _tw = (_w * _th)/float(_h)
        tblock.setBounds(_tw, _th)
        tblock.setFontScale(1/float(pango.SCALE))
        _layout = None
        return
    # print "TextBlock pixel height: %g [%d]" % (_ph, _iph)
    _w, _h = _layout.get_pixel_size()
    # print "first layout: w: %d; h: %d" % (_w, _h)
    _i = 0
    if _h != _iph:
        #
        # loop until the layout pixel height equals the "correct" pixel height
        #
        _diff = abs(_h - _iph)
        _ofs = _fs
        _fs = (_fs * _ph)/float(_h)
        # print "adjusted font size: %g" % (_fs)
        while True:
            try:
                _text=util.to_unicode(_text)
            except:
                print "Debug: Unable to unicode %s"%str(_text)
                _text='Error on converting in unicode'
            _layout = _da.create_pango_layout(_text)
            _fd = pango.FontDescription()
            _fd.set_family(_family)
            _fd.set_style(_style)
            _fd.set_weight(_weight)
            _fd.set_size(int(pango.SCALE * _fs))
            _layout.set_font_description(_fd)
            _w, _h = _layout.get_pixel_size()
            # print "adjusted layout: w: %d; h: %d" % (_w, _h)
            #
            # tests to bail out
            #
            # all the inexact comparisons and iteration max
            # count text are arbitrary ...
            #
            if _h == _iph:
                # print "exact match"
                break
            if ((_iph > 10) and (abs(_iph - _h) < 2)):
                # print "within 2"
                break
            if ((_iph > 100) and (abs(_iph - _h) < 10)):
                # print "within 10"
                break
            if ((_iph > 1000) and (abs(_iph - _h) < 40)):
                # print "within 40"
                break
            if _i > 25:
                # print "25 iterations"
                break
            #
            # bah, another iteration
            #
            _d = abs(_h - _iph)
            if  _d < _diff:
                _diff = _d
                _ofs = _fs
                _fs = (_fs * _ph)/float(_h)
            else:
                # split the difference in the changed font size
                # and try again, but do not reset the old font
                # size
                _fs = _ofs + ((_fs - _ofs)/2.0)
            # print "adjusted font size: %g" % (_fs)
            _i = _i + 1
    #
    # with the layout sized "correctly", calculate the TextBlock width
    #
    _w, _h = _layout.get_size()
    _tw = (_w * _th)/float(_h)
    # print "TextBlock width: %g" % _tw
    tblock.setBounds(_tw, _th)
    tblock.setFontScale(_fs)
    _layout = None
    
def _make_pango_layout(gtkimage, text, family, style, weight, size):
    _layout = gtkimage.getDA().create_pango_layout(text)
    _fd = pango.FontDescription()
    _fd.set_family(family)
    if style == TextStyle.FONT_NORMAL:
        _style = pango.STYLE_NORMAL
    elif style == TextStyle.FONT_OBLIQUE:
        _style = pango.STYLE_OBLIQUE
    elif style == TextStyle.FONT_ITALIC:
        _style = pango.STYLE_ITALIC
    else:
        raise ValueError, "Unexpected font style: %d" % style
    _fd.set_style(_style)
    if weight == TextStyle.WEIGHT_NORMAL:
        _weight = pango.WEIGHT_NORMAL
    elif weight == TextStyle.WEIGHT_LIGHT:
        _weight = pango.WEIGHT_LIGHT
    elif weight == TextStyle.WEIGHT_BOLD:
        _weight = pango.WEIGHT_BOLD
    elif weight == TextStyle.WEIGHT_HEAVY:
        _weight = pango.WEIGHT_HEAVY
    else:
        raise ValueError, "Unexpected font weight: %d" % weight
    _fd.set_weight(_weight)
    _sz = int(pango.SCALE * (size/gtkimage.getUnitsPerPixel()))
    if _sz < pango.SCALE:
        _sz = pango.SCALE
    _fd.set_size(_sz)
    _layout.set_font_description(_fd)
    return _layout
    
def text_add_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Enter text'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _tb = gtk.TextBuffer()
    _tv = gtk.TextView(_tb)
    _sw = gtk.ScrolledWindow()
    _sw.set_size_request(400, 300)
    _sw.add_with_viewport(_tv)
    _dialog.vbox.pack_start(_sw, False, False, 0)
    _dialog.show_all()
    _text = None
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _start_iter, _end_iter = _tb.get_bounds()
        _text = _tb.get_text(_start_iter, _end_iter)
    _dialog.destroy()
    return _text

