#
# Copyright (c) 2006 Art Haas
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
# Foundation, Inc., 51 Franklin Stree, Fifth Floor, Boston, MA 02110-1301,
# USA
#
#
# code for displaying Style values
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sys

from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import image

class GtkStyle(object):
    """
    """
    def __init__(self, window, gs=None):
        if not isinstance(window, gtk.Window):
            raise TypeError, "Invalid window type: " + `type(window)`
        self.__window = window
        self.__widgets = {}
        self.__styles = []
        self.__linetypes = []
        self.__style = None
        if gs is not None:
            self.setStyle(gs)

    def addStyle(self, s):
        """Store a Style in the GtkStyle

addStyle(s)

Argument 's' must be a Style instance.
        """
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid Style: " + `type(s)`
        self.__styles.append(s)

    def addLinetype(self, l):
        """
        """
        if not isinstance(l, linetype.Linetype):
            raise TypeError, "Invalid Linetype: " + `type(l)`
        self.__linetypes.append(l)
        
    def getStyles(self):
        """Return the list of stored Styles.

getStyles()

This method returns a list of Style instances stored
with the addStyle() method.
        """
        return self.__styles

    def getLinetypes(self):
        """Return the list of stored Linetypes

getLinetypes()

This method returns a list of Linetype instances stored
with the addLinetype() method.
        """
        return self.__linetypes
    
    def setStyle(self, s):
        """Set the Style defining the various widget values.

setTextStyle(ts)

Argument 's' must be a Style instance.
        """
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid Style: " + `type(s)`
        self.__style = s
        self.setValues()

    def getStyle(self):
        """Get the Style used to define the widget values.

getStyle()

This method returns a Style instance or None if no Style
has been stored in the GtkStyle instance.
        """
        return self.__style

    def __selectColor(button, s=None):
        _s = s
        if _s is None:
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
            _da.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(_str))
        _dialog.destroy()

    __selectColor = staticmethod(__selectColor)

    def __moveCursor(entry):
        entry.set_position(-1)
        return False

    __moveCursor = staticmethod(__moveCursor)

    def __entryActivate(entry):
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

    __entryActivate = staticmethod(__entryActivate)

    def __entryFocusOut(entry, event, text=''):
        _text = entry.get_text()
        if _text == '' or _text == '+':
            _thickness = entry.get_data('thickness')
            _hid = entry.get_data('handlerid')
            entry.delete_text(0, -1)
            entry.handler_block(_hid)
            try:
                entry.set_text(_thickness)
            finally:
                entry.handler_unblock(_hid)
        return False

    __entryFocusOut = staticmethod(__entryFocusOut)

    def __entryInsertText(entry, new_text, new_text_length, position):
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
                    gobject.idle_add(GtkStyle.__moveCursor, entry)
                else:
                    gtk.idle_add(GtkStyle.__moveCursor, entry)
        entry.stop_emission("insert-text")

    __entryInsertText = staticmethod(__entryInsertText)

    def __getColorDA(widgets, key, val, s=None):
        _widget = widgets.get(key)
        if _widget is None:
            _widget = gtk.Button()
            _frame = gtk.Frame()
            _frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
            _frame.set_border_width(5)
            _widget.add(_frame)
            _da = gtk.DrawingArea()
            _da.set_size_request(20, 10)
            _widget.connect('clicked', GtkStyle.__selectColor, s)
            _frame.add(_da)
        else:
            _da = _widget.get_child().get_child()
        _da.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(str(val)))
        return _widget

    __getColorDA = staticmethod(__getColorDA)

    def __getColorButton(widgets, key, val, s):
        _widget = widgets.get(key)
        if _widget is None:
            _widget = gtk.ColorButton()
            _widget.set_title(s)
        _widget.set_color(gtk.gdk.color_parse(str(val)))
        return _widget

    __getColorButton = staticmethod(__getColorButton)

    def __getOptionMenu(widgets, key, val, entries):
        _widget = widgets.get(key)
        if _widget is None:
            _widget = gtk.OptionMenu()
            _menu = gtk.Menu()
        else:
            _menu = _widget.getMenu()
            for _child in _menu.get_children():
                _menu.remove(_child)
        _idx = 0
        for _i in range(len(entries)):
            _name, _val = entries[_i]
            if _val == val:
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
        return _widget

    __getOptionMenu = staticmethod(__getOptionMenu)

    def __getComboBox(widgets, key, val, entries):
        _widget = widgets.get(key)
        if _widget is None:
            _widget = gtk.combo_box_new_text()
        else:
            _model = _widget.get_model()
            if _model is not None:
                while len(_model):
                    _widget.remove_text(0)
        _idx = 0
        for _i in range(len(entries)):
            _val = entries[_i]
            if _val == val:
                _idx = _i
            _widget.append_text(_val)
        _widget.set_active(_idx)
        return _widget

    __getComboBox = staticmethod(__getComboBox)

    def setValues(self):
        """Store the TextStyle values in the interface widgets.

setValues()
        """
        _s = self.__style
        if _s is None:
            raise RuntimeError, "No Style defined for the GtkStyle instance."
        _widgets = self.__widgets
        #
        _key = 'LINE_TYPE'
        _widget = _widgets.get(_key)
        _lt = _s.getLinetype()
        _ltname = _lt.getName()
        _lts = self.__linetypes
        if hasattr(gtk, 'ComboBox'):
            if _widget is None:
                _widget = gtk.combo_box_new_text()
            else:
                _model = _widget.get_model()
                if _model is not None:
                    while len(_model):
                        _widget.remove_text(0)
            _idx = 0
            for _i in range(len(_lts)):
                _val = _lts[_i]
                _vname = _val.getName()
                if _vname == _ltname:
                    _idx = _i
                _widget.append_text(_vname)
            _widget.set_active(_idx)
        else:
            if _widget is None:
                _widget = gtk.OptionMenu()
                _menu = gtk.Menu()
            else:
                _menu = _widget.getMenu()
                for _child in _menu.get_children():
                    _menu.remove(_child)
            _idx = 0
            for _i in range(len(_lts)):
                _val = _lts[_i]
                _vname = _val.getName()
                if _vname == _ltname:
                    _idx = _i
                _item = gtk.MenuItem(_vname)
                _menu.append(_item)
            _widget.set_menu(_menu)
            _widget.set_history(_idx)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _val = _s.getColor()
        _str = _('Select Color')
        if hasattr(gtk, 'ColorButton'):
            _sm = GtkStyle.__getColorButton
        else:
            _sm = GtkStyle.__getColorDA
        _key = 'LINE_COLOR'
        _widget = _sm(_widgets, _key, _val, _str)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'LINE_THICKNESS'
        _entry = _widgets.setdefault(_key, gtk.Entry())
        _val = _s.getThickness()
        _size = "%f" % _val
        _entry.set_data('thickness', _val)
        _hid = _entry.get_data('handlerid')
        if _hid is not None:
            _entry.handler_block(_hid)
            try:
                _entry.set_text(_size)
            finally:
                _entry.handler_unblock(_hid)
        else:
            _entry.set_text(_size)
            _handlerid = _entry.connect('insert-text',
                                        GtkStyle.__entryInsertText)
            _entry.set_data('handlerid', _handlerid)
            _entry.connect('activate', GtkStyle.__entryActivate)
            _entry.connect('focus-out-event',
                           GtkStyle.__entryFocusOut)
        if _key not in _widgets:
            _widgets[_key] = _entry
            
    def __getRGBValues(color):
        if not isinstance(color, gtk.gdk.Color):
            raise TypeError, "Unexpected color type: " + `type(color)`
        _r = int(round((color.red/65535.0) * 255.0))
        _g = int(round((color.green/65535.0) * 255.0))
        _b = int(round((color.blue/65535.0) * 255.0))
        return _r, _g, _b

    __getRGBValues = staticmethod(__getRGBValues)

    def setImageSettings(self, im):
        """Store the Image settings of various Style values.

setImageSettings(im)

Argument 'im' must be and Image instance.
        """
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        _widgets = self.__widgets
        #
        _key = 'LINE_TYPE'
        _widget = _widgets.get(_key)
        _lt = im.getOption(_key)
        _ltname = _lt.getName()
        _lts = self.__linetypes
        if hasattr(gtk, 'ComboBox'):
            if _widget is None:
                _widget = gtk.combo_box_new_text()
            else:
                _model = _widget.get_model()
                if _model is not None:
                    while len(_model):
                        _widget.remove_text(0)
            _idx = 0
            for _i in range(len(_lts)):
                _val = _lts[_i]
                _vname = _val.getName()
                if _vname == _ltname:
                    _idx = _i
                _widget.append_text(_vname)
            _widget.set_active(_idx)
        else:
            if _widget is None:
                _widget = gtk.OptionMenu()
                _menu = gtk.Menu()
            else:
                _menu = _widget.getMenu()
                for _child in _menu.get_children():
                    _menu.remove(_child)
            _idx = 0
            for _i in range(len(_lts)):
                _val = _lts[_i]
                _vname = _val.getName()
                if _vname == _ltname:
                    _idx = _i
                _item = gtk.MenuItem(_vname)
                _menu.append(_item)
            _widget.set_menu(_menu)
            _widget.set_history(_idx)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'LINE_COLOR'
        _val = im.getOption(_key)
        _str = _('Select Color')
        if hasattr(gtk, 'ColorButton'):
            _sm = GtkStyle.__getColorButton
        else:
            _sm = GtkStyle.__getColorDA
        _widget = _sm(_widgets, _key, _val, _str)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'LINE_THICKNESS'
        _entry = _widgets.setdefault(_key, gtk.Entry())
        _val = im.getOption(_key)
        _size = "%f" % _val
        _entry.set_data('thickness', _val)
        _hid = _entry.get_data('handlerid')
        if _hid is not None:
            _entry.handler_block(_hid)
            try:
                _entry.set_text(_size)
            finally:
                _entry.handler_unblock(_hid)
        else:
            _entry.set_text(_size)
            _handlerid = _entry.connect('insert-text',
                                        GtkStyle.__entryInsertText)
            _entry.set_data('handlerid', _handlerid)
            _entry.connect('activate', GtkStyle.__entryActivate)
            _entry.connect('focus-out-event',
                           GtkStyle.__entryFocusOut)
        if _key not in _widgets:
            _widgets[_key] = _entry

    def getValues(self):
        """Return the values stored in the widgets

getValues()

This method returns a list of tuples in the form (key, value),
where 'key' is the Style option and 'value' is the option value.
        """
        _s = self.__style
        if _s is None:
            raise RuntimeError, "No Style defined for the GtkStyle instance."
        _values = []
        _widgets = self.__widgets
        #
        _key = 'LINE_TYPE'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ComboBox'):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, self.__linetypes[_idx]))
        #
        _key = 'LINE_COLOR'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ColorButton'):
            _color = _widget.get_color()
        elif isinstance(_widget, gtk.Button):
            _da = _widget.getChild().getChild()
            _color= _da.get_style().bg[gtk.STATE_NORMAL]
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, GtkStyle.__getRGBValues(_color)))
        _key = 'LINE_THICKNESS'
        _widget = _widgets[_key]
        _text = _widget.get_text()
        if len(_text) and _text != '+':
            _value = float(_text)
        else:
            _value = _s.getThickness()
        _values.append((_key, _value))
        return _values
        
    def getWidget(self, key):
        """Return a widget associated with a Style option.

getWidget(key)

Argument 'key' must be a valid Style option key. This method
returns a widget or None.
        """
        if (key != 'LINE_TYPE' and 
            key != 'LINE_COLOR' and
            key != 'LINE_THICKNESS'):
            return ValueError, "Invalid Style key: " + key
        return self.__widgets.get(key)

    def clear(self):
        """Clear out all values and widgets in the GtkStyle.

clear()        
        """
        self.__window = None
        self.__widgets.clear()
        del self.__styles[:]
        del self.__linetypes[:]
        self.__style = None

def _widget_changed(widget, gs):
    if hasattr(gtk, 'ComboBox'):
        _idx = widget.get_active()
    else:
        _idx = widget.get_history()
    _styles = gs.getStyles()
    gs.setStyle(_styles[_idx])

def _fill_dialog(dvbox, gs):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Graphic Properties'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Linetype:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gs.getWidget('LINE_TYPE')
    _hbox.pack_start(_widget, False, False, 2)
    # 
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gs.getWidget('LINE_COLOR')
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Thickness:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gs.getWidget('LINE_THICKNESS')
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)
    
def style_dialog(gtkimage, styles, linetypes):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Style Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _st = _image.getOption('LINE_STYLE')
    _hbox = gtk.HBox(False, 5)
    _hbox.set_border_width(5)
    _label = gtk.Label(_('Active Style:'))
    _hbox.pack_start(_label, False, False, 5)
    _idx = 0
    if hasattr(gtk, 'ComboBox'):
        _widget = gtk.combo_box_new_text()
        for _i in range(len(styles)):
            _style = styles[_i]
            if (_st is _style or
                _st == _style):
                _idx = _i
            _widget.append_text(_style.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(styles)):
            _style = styles[_i]
            if (_st is _style or
                _st == _style):
                _idx = _i
            _item = gtk.MenuItem(_style.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    _hbox.pack_start(_widget, False, False, 0)
    _dialog.vbox.pack_start(_hbox, True, True)
    #
    _gs = GtkStyle(_window)
    for _style in styles:
        _gs.addStyle(_style)
    for _lt in linetypes:
        _gs.addLinetype(_lt)
    _gs.setStyle(_st)
    _gs.setImageSettings(_image)
    _fill_dialog(_dialog.vbox, _gs)
    _widget.connect('changed', _widget_changed, _gs)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _nst = _gs.getStyle()
        if _nst != _st:
            _image.setOption('LINE_STYLE', _nst)
        for _opt, _val in _gs.getValues():
            if _opt == 'LINE_TYPE':
                if _val != _image.getOption(_opt):
                    _image.setOption(_opt, _val)
            elif _opt == 'LINE_COLOR':
                if _val != _image.getOption(_opt).getColors():
                    _r, _g, _b = _val
                    _image.setOption(_opt, color.Color(_r, _g, _b))
            elif _opt == 'LINE_THICKNESS':
                if abs(_val - _image.getOption(_opt)) > 1e-10:
                    _image.setOption(_opt, _val)
            else:
                raise RuntimeError, "Unexpected TextStyle option '%s'" % _opt
    _gs.clear()
    _dialog.destroy()
