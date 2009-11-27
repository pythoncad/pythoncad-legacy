#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
#
#               2009 Matteo Boscolo
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
# menu functions for creating entities in drawing
# like segments, circles, etc ...
#

from math import hypot, pi, atan2

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import math

import sys

from PythonCAD.Generic import globals
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import color
from PythonCAD.Generic import util
from PythonCAD.Generic import units
from PythonCAD.Interface.Gtk import gtkDialog
from PythonCAD.Generic import tools   
from PythonCAD.Generic import snap
from PythonCAD.Interface.Command import cmdCommon

#
# set the active style
#

def set_active_style(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Active Style'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Style:'))
    _image = gtkimage.getImage()
    _cur_style = _image.getOption('LINE_STYLE')
    _styles = _image.getImageEntities("style")
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cur_style:
                _idx = _i
            _widget.append_text(_s.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_styles)):
            _s = _styles[_i]
            if _s is _cur_style:
                _idx = _i
            _item = gtk.MenuItem(_s.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_label, False, False, 0)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _image.setOption('LINE_STYLE', _styles[_idx])
    _dialog.destroy()

#
# set the current color
#

def set_active_color(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.ColorSelectionDialog(_('Set Active Color'))
    _dialog.set_transient_for(_window)
    _colorsel = _dialog.colorsel
    _image = gtkimage.getImage()
    _prev_color = _image.getOption('LINE_COLOR')
    _gtk_color = gtkimage.getColor(_prev_color)
    _colorsel.set_previous_color(_gtk_color)
    _colorsel.set_current_color(_gtk_color)
    _colorsel.set_has_palette(True)
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _gtk_color = _colorsel.get_current_color()
        _r = int(round((_gtk_color.red/65535.0) * 255.0))
        _g = int(round((_gtk_color.green/65535.0) * 255.0))
        _b = int(round((_gtk_color.blue/65535.0) * 255.0))
        _color = None
        for _c in _image.getImageEntities('color'):
            if _c.r == _r and _c.g == _g and _c.b == _b:
                _color = _c
                break
        if _color is None:
            _color = color.Color(_r, _g, _b)
        _image.setOption('LINE_COLOR', _color)
    _dialog.destroy()

#
# set the current linetype
#

def set_active_linetype(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Active Linetype'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)

    _label = gtk.Label(_('Linetype:'))
    _hbox.pack_start(_label, False, False, 0)
    _image = gtkimage.getImage()
    _cur_linetype = _image.getOption('LINE_TYPE')
    _linetypes = _image.getImageEntities("linetype")
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _cur_linetype:
                _idx = _i
            _widget.append_text(_lt.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_linetypes)):
            _lt = _linetypes[_i]
            if _lt is _cur_linetype:
                _idx = _i
            _item = gtk.MenuItem(_lt.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_widget, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if isinstance(_widget, gtk.ComboBox):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget: " + `type(_widget)`
        _image.setOption('LINE_TYPE', _linetypes[_idx])
    _dialog.destroy()

#
# set the current line thickness
#

def move_cursor(entry):
    entry.set_position(-1)
    return False

def thickness_activate(entry): # this probably isn't a good choice ...
    entry.stop_emission("activate")

def thickness_focus_out(entry, event):
    _text = entry.get_text()
    if _text == '-' or _text == '+':
        entry.delete_text(0, -1)
    return False

def thickness_insert_text(entry, new_text, new_text_length, position):
    if (new_text.isdigit() or
        new_text == '.' or
        new_text == '+'):
        _string = entry.get_text() + new_text[:new_text_length]
        _hid = entry.get_data('handlerid')
        entry.handler_block(_hid)
        try:
            _pos = entry.get_position()
            if _string == '+':
                _pos = entry.insert_text(new_text, _pos)
            else:
                try:
                    _val = float(_string)
                    _pos = entry.insert_text(new_text, _pos)
                except StandardError, e:
                    pass
        finally:
            entry.handler_unblock(_hid)
        if hasattr(gobject, 'idle_add'):
            gobject.idle_add(move_cursor, entry)
        else:
            gtk.idle_add(move_cursor, entry)
    entry.stop_emission("insert-text")

def set_line_thickness(gtkimage):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Set Line Thickness'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK,
                          gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL,
                          gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _label = gtk.Label(_('Thickness:'))
    _hbox.pack_start(_label, False, False, 0)
    _image = gtkimage.getImage()
    _thickness = "%g" % _image.getOption('LINE_THICKNESS')
    _entry = gtk.Entry()
    _entry.set_text(_thickness)
    _entry.connect("focus_out_event", thickness_focus_out)
    _entry.connect("activate", thickness_activate)
    _handlerid = _entry.connect("insert-text", thickness_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _hbox.pack_start(_entry, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _text = _entry.get_text()
        _thickness = float(_text)
        _image.setOption('LINE_THICKNESS', _thickness)
    _dialog.destroy()

#

def _selectColor(button):
    _s = _('Select Color')
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_s)
    _colorsel = _dialog.colorsel
    _colorsel.set_previous_color(_color)
    _colorsel.set_current_color(_color)
    _colorsel.set_has_palette(True)
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _r, _g, _b = _get_rgb_values(_colorsel.get_current_color())
        _str = "#%02x%02x%02x" % (_r, _g, _b)
        _color = gtk.gdk.color_parse(_str)
        _da.modify_bg(gtk.STATE_NORMAL, _color)
    _dialog.destroy()

def _fill_color_dialog(dvbox, widgets):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Color Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Inactive Layer Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['INACTIVE_LAYER_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Background Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['BACKGROUND_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Single Point Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['SINGLE_POINT_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Multi-Point Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['MULTI_POINT_COLOR']
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)    

def _selectColor(button):
    _s = _('Select Color')
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_s)
    _colorsel = _dialog.colorsel
    _colorsel.set_previous_color(_color)
    _colorsel.set_current_color(_color)
    _colorsel.set_has_palette(True)
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _r, _g, _b = _get_rgb_values(_colorsel.get_current_color())
        _str = "#%02x%02x%02x" % (_r, _g, _b)
        _color = gtk.gdk.color_parse(_str)
        _da.modify_bg(gtk.STATE_NORMAL, _color)
    _dialog.destroy()

def _get_color_da():
    _widget = gtk.Button()
    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
    _frame.set_border_width(5)
    _widget.add(_frame)
    _da = gtk.DrawingArea()
    _da.set_size_request(20, 10)
    _widget.connect('clicked', _select_color)
    _frame.add(_da)
    return _widget

def _get_widget(col):
    if hasattr(gtk, 'ColorButton'):
        _widget = gtk.ColorButton()
        _widget.set_color(col)
    else:
        _widget = _get_color_da()
        _widget.modify_bg(gtk.STATE_NORMAL, col)
    return _widget

def _get_color_widgets(opts, im):
    _widgets = {}
    for _opt in opts:
        _color = gtk.gdk.color_parse(str(im.getOption(_opt)))
        _widgets[_opt] = _get_widget(_color)
    return _widgets

def _get_color(widgets, key):
    _widget = widgets[key]
    if hasattr(gtk, 'ColorButton'):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.Button):
        _da = _widget.getChild().getChild()
        _color= _da.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
    return _color
    
def set_colors_dialog(gtkimage):
    _opts = ['INACTIVE_LAYER_COLOR',
             'BACKGROUND_COLOR',
             'SINGLE_POINT_COLOR',
             'MULTI_POINT_COLOR']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Color Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = _get_color_widgets(_opts, _image)
    _fill_color_dialog(_dialog.vbox, _widgets)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _color = _get_color(_widgets, _opt)
            _r = int(round((_color.red/65535.0) * 255.0))
            _g = int(round((_color.green/65535.0) * 255.0))
            _b = int(round((_color.blue/65535.0) * 255.0))
            if (_r, _g, _b) != _image.getOption(_opt).getColors():
                _image.setOption(_opt, color.Color(_r, _g, _b))
    _widgets.clear()
    _dialog.destroy()

#

def _size_move_cursor(entry):
    entry.set_position(-1)
    return False

def _size_entry_activate(entry):
    _text = entry.get_text()
    entry.delete_text(0, -1)
    if len(_text):
        if _text == '-' or _text == '+':
            sys.stderr.write("Incomplete value: '%s'\n" % _text)
        else:
            try:
                _value = float(_text)
            except:
                sys.stderr.write("Invalid float: '%s'\n" % _text)
    else:
        sys.stderr.write("Empty entry box.")

def _size_entry_focus_out(entry, event, text=''):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        _size = entry.get_data('size')
        _hid = entry.get_data('handlerid')
        entry.delete_text(0, -1)
        entry.handler_block(_hid)
        try:
            entry.set_text(_size)
        finally:
            entry.handler_unblock(_hid)
    return False

def _size_entry_insert_text(entry, new_text, new_text_length, position):
    if (new_text.isdigit() or
        new_text == '.' or
        new_text == '+'):
        _string = entry.get_text() + new_text[:new_text_length]
        _hid = entry.get_data('handlerid')
        _move = True
        entry.handler_block(_hid)
        try:
            _pos = entry.get_position()
            if _string == '+':
                _pos = entry.insert_text(new_text, _pos)
            else:
                try:
                    _val = float(_string)
                except StandardError, e:
                    _move = False
                else:
                    _pos = entry.insert_text(new_text, _pos)
        finally:
            entry.handler_unblock(_hid)
        if _move:
            if hasattr(gobject, 'idle_add'):
                gobject.idle_add(_size_move_cursor, entry)
            else:
                gtk.idle_add(_size_move_cursor, entry)
    entry.stop_emission('insert-text')

def _fill_size_dialog(dvbox, widgets):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Size Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Chamfer length:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['CHAMFER_LENGTH']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Fillet Radius:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['FILLET_RADIUS']
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Leader Arrow Size:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = widgets['LEADER_ARROW_SIZE']
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)    

def set_sizes_dialog(gtkimage):
    _opts = ['CHAMFER_LENGTH',
             'FILLET_RADIUS',
             'LEADER_ARROW_SIZE']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Size Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = {}
    for _opt in _opts:
        _val = _image.getOption(_opt)
        _entry = gtk.Entry()
        _sval = "%f" % _val
        _entry.set_data('size', _sval)
        _entry.set_text(_sval)
        _handlerid = _entry.connect('insert-text', _size_entry_insert_text)
        _entry.set_data('handlerid', _handlerid)
        _entry.connect('activate', _size_entry_activate)
        _entry.connect('focus-out-event', _size_entry_focus_out)
        _widgets[_opt] = _entry
    _fill_size_dialog(_dialog.vbox, _widgets)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _text = _widgets[_opt].get_text()
            _ival = _image.getOption(_opt)
            if len(_text) and _text != '+':
                _value = float(_text)
            else:
                _value = _ival
            if abs(_value - _ival) > 1e-10:
                _image.setOption(_opt, _value)
    _widgets.clear()
    _dialog.destroy()

#

def set_toggle_dialog(gtkimage):
    _opts = ['AUTOSPLIT', 'HIGHLIGHT_POINTS']
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Operation Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _widgets = {}
    for _opt in _opts:
        _val = _image.getOption(_opt)
        if _opt == 'AUTOSPLIT':
            _str = _('New Points split existing entities')
        else:
            _str = _('Boxes are drawn around Point objects')
        _cb = gtk.CheckButton(_str)
        _cb.set_active(_val)
        _widgets[_opt] = _cb
    _frame = gtk.Frame(_('Operation Settings'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    _vbox.pack_start(_widgets['AUTOSPLIT'], True, True, 2)
    _vbox.pack_start(_widgets['HIGHLIGHT_POINTS'], True, True, 2)
    _dialog.vbox.pack_start(_frame, False, False, 2)            
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        for _opt in _opts:
            _val = _widgets[_opt].get_active()
            _image.setOption(_opt, _val)
    _widgets.clear()
    _dialog.destroy()

def set_units_dialog(gtkimage):
    _units = units.Unit.getUnitStrings()
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Image Units'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _unit = _image.getUnits()
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_units)):
            _ui = _units[_i]
            if _unit == units.Unit.getUnitFromString(_ui):
                _idx = _i
            _widget.append_text(_ui)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_units)):
            _ui = _units[_i]
            if _unit is _units.Unit.getUnitFromString(_ui):
                _idx = _i
            _item = gtk.MenuItem(_ui)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _vbox = _dialog.vbox
    _vbox.set_border_width(5)
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Units:'))
    _hbox.pack_start(_label, False, False, 2)
    _hbox.pack_start(_widget, False, False, 2)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        if hasattr(gtk, 'ComboBox'):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget " + `type(_widget)`
        _val = units.Unit.getUnitFromString(_units[_idx])
        if _val != _unit:
            _image.setUnits(_val)
    _dialog.destroy()
    
