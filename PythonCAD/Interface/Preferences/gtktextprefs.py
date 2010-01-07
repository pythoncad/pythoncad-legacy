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
# code for displaying TextStyle values
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sys

from PythonCAD.Generic import color
from PythonCAD.Generic import units
from PythonCAD.Generic import text
from PythonCAD.Generic import image

class GtkTextStyle(object):
    """
    """
    __font_styles = text.TextStyle.getStyleStrings()
    __font_weights = text.TextStyle.getWeightStrings()
    __text_align = text.TextStyle.getAlignmentStrings()
    __families = None

    def __init__(self, window, ts=None):
        if not isinstance(window, gtk.Window):
            raise TypeError, "Invalid window type: " + `type(window)`
        self.__window = window
        self.__widgets = {}
        self.__textstyles = []
        self.__ts = None
        if ts is not None:
            self.setTextStyle(ts)

    def addTextStyle(self, ts):
        """Store a TextStyle in the GtkTextStyle

addTextStyle(ts)

Argument 'ts' must be a TextStyle instance.
        """
        if not isinstance(ts, text.TextStyle):
            raise TypeError, "Invalid TextStyle: " + `type(ts)`
        self.__textstyles.append(ts)

    def getTextStyles(self):
        """Return the list of stored TextStyles.

getTextStyles()

This method returns a list of TextStyle instances stored
with the addTextStyle() method.
        """
        return self.__textstyles

    def setTextStyle(self, ts):
        """Set the TextStyle defining the various widget values.

setTextStyle(ts)

Argument 'ts' must be a TextStyle instance.
        """
        if not isinstance(ts, text.TextStyle):
            raise TypeError, "Invalid TextStyle: " + `type(ts)`
        self.__ts = ts
        self.setValues()

    def getTextStyle(self):
        """Get the TextStyle used to define the widget values.

getTextStyle()

This method returns a TextStyle instance or None if no TextStyle
has been stored in the GtkTextStyle instance.
        """
        return self.__ts
    
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
            _color = gtk.gdk.color_parse(_str)
            _da.modify_bg(gtk.STATE_NORMAL, _color)
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
            _size = entry.get_data('size')
            _hid = entry.get_data('handlerid')
            entry.delete_text(0, -1)
            entry.handler_block(_hid)
            try:
                entry.set_text(_size)
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
                    gobject.idle_add(GtkTextStyle.__moveCursor, entry)
                else:
                    gtk.idle_add(GtkTextStyle.__moveCursor, entry)
        entry.stop_emission('insert-text')

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
            _widget.connect('clicked', GtkTextStyle.__selectColor, s)
            _frame.add(_da)
        else:
            _da = _widget.get_child().get_child()
        _da.modify_bg(gtk.STATE_NORMAL, val)
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
            _val = entries[_i]
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
        _ts = self.__ts
        if _ts is None:
            raise RuntimeError, "No TextStyle defined for the GtkTextStyle instance."
        _widgets = self.__widgets
        #
        if GtkTextStyle.__families is None:
            _families = []
            for _family in self.__window.get_pango_context().list_families():
                _families.append(_family.get_name())
            _families.sort()
            GtkTextStyle.__families = _families
        _val = _ts.getFamily()
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _key = 'FONT_FAMILY'            
        _widget = _sm(_widgets, _key, _val, GtkTextStyle.__families)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _val = _ts.getStyle()
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _key = 'FONT_STYLE'
        _widget = _sm(_widgets, _key, _val, GtkTextStyle.__font_styles)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _val = _ts.getWeight()
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _key = 'FONT_WEIGHT'
        _widget = _sm(_widgets, _key, _val, GtkTextStyle.__font_weights)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _val = _ts.getColor()
        _s = _('Select Font Color')
        if hasattr(gtk, 'ColorButton'):
            _sm = GtkTextStyle.__getColorButton
        else:
            _sm = GtkTextStyle.__getColorDA
        _key = 'FONT_COLOR'
        _widget = _sm(_widgets, _key, _val, _s)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        # fixme - TEXT_ANGLE
        #
        _val = _ts.getAlignment()
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _key = 'TEXT_ALIGNMENT'
        _widget = _sm(_widgets, _key, _val, GtkTextStyle.__text_align)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'TEXT_SIZE'
        _entry = _widgets.setdefault(_key, gtk.Entry())
        _val = _ts.getSize()        
        _size = "%f" % _val
        _entry.set_data('size', _size)
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
                                        GtkTextStyle.__entryInsertText)
            _entry.set_data('handlerid', _handlerid)
            _entry.connect('activate', GtkTextStyle.__entryActivate)
            _entry.connect('focus-out-event',
                           GtkTextStyle.__entryFocusOut)
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

    def getValues(self):
        """Return the values stored in the widgets

getValues()

This method returns a list of tuples in the form (key, value),
where 'key' is the TextStyle option and 'value' is the option value.
        """
        _ts = self.__ts
        if _ts is None:
            raise RuntimeError, "No TextStyle defined for the GtkTextStyle instance."
        _values = []
        _widgets = self.__widgets
        #
        _key = 'FONT_FAMILY'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ComboBox'):
            _idx = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _idx = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, GtkTextStyle.__families[_idx]))
        #
        _key = 'FONT_WEIGHT'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ComboBox'):
            _value = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _value = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, _value))
        #
        _key = 'FONT_STYLE'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ComboBox'):
            _value = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _value = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, _value))
        #
        _key = 'FONT_COLOR'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ColorButton'):
            _color = _widget.get_color()
        elif isinstance(_widget, gtk.Button):
            _da = _widget.getChild().getChild()
            _color= _da.get_style().bg[gtk.STATE_NORMAL]
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, GtkTextStyle.__getRGBValues(_color)))
        
        #
        _key = 'TEXT_ALIGNMENT'
        _widget = _widgets[_key]
        if hasattr(gtk, 'ComboBox'):
            _value = _widget.get_active()
        elif isinstance(_widget, gtk.OptionMenu):
            _value = _widget.get_history()
        else:
            raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
        _values.append((_key, _value))
        #
        _key = 'TEXT_SIZE'
        _widget = _widgets[_key]
        _text = _widget.get_text()
        if len(_text) and _text != '+':
            _value = float(_text)
        else:
            _value = _ts.getSize()
        _values.append((_key, _value))
        #
        # fixme - TEXT_ANGLE
        #
        return _values
        
    def getWidget(self, key):
        """Return a widget associated with a TextStyle option.

getWidget(key)

Argument 'key' must be a valid TextStyle option key. This method
returns a widget or None.
        """
        if (key != 'FONT_FAMILY' and
            key != 'FONT_STYLE' and
            key != 'FONT_WEIGHT' and
            key != 'FONT_COLOR' and
            key != 'TEXT_SIZE' and
            key != 'TEXT_ALIGNMENT' and
            key != 'TEXT_ANGLE'):
            return ValueError, "Invalid TextStyle key: " + key
        return self.__widgets.get(key)

    def clear(self):
        """Clear out all values and widgets in the GtkTextStyle.

clear()        
        """
        self.__window = None
        self.__widgets.clear()
        del self.__textstyles[:]
        self.__ts = None

    def setImageSettings(self, im):
        """Adjust the widgets values based on current Image values

setImageSettings(im)

Argument 'im' must be an Image instance.
        """
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        _widgets = self.__widgets
        _key = 'FONT_FAMILY'
        _ival = im.getOption(_key)
        if GtkTextStyle.__families is None:
            _families = []
            for _family in self.__window.get_pango_context().list_families():
                _families.append(_family.get_name())
            _families.sort()
            GtkTextStyle.__families = _families
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _widget = _sm(_widgets, _key, _ival, GtkTextStyle.__families)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'FONT_STYLE'
        _ival = im.getOption(_key)
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _optlist = GtkTextStyle.__font_styles
        _widget = _sm(_widgets, _key, _ival, _optlist)
        _idx = 0
        for _i in range(len(_optlist)):
            _val = text.TextStyle.getStyleFromString(_optlist[_i])
            if _val == _ival:
                _idx = _i
        _widget.set_active(_idx)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'FONT_WEIGHT'
        _ival = im.getOption(_key)
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _optlist = GtkTextStyle.__font_weights
        _widget = _sm(_widgets, _key, _ival, _optlist)
        _idx = 0
        for _i in range(len(_optlist)):
            _val = text.TextStyle.getWeightFromString(_optlist[_i])
            if _val == _ival:
                _idx = _i
        _widget.set_active(_idx)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'FONT_COLOR'
        _ival = im.getOption(_key)
        _s = _('Select Font Color')
        if hasattr(gtk, 'ColorButton'):
            _sm = GtkTextStyle.__getColorButton
        else:
            _sm = GtkTextStyle.__getColorDA
        _widget = _sm(_widgets, _key, _ival, _s)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        # fixme - TEXT_ANGLE
        #
        _key = 'TEXT_ALIGNMENT'
        _ival = im.getOption(_key)
        if hasattr(gtk, 'ComboBox'):
            _sm = GtkTextStyle.__getComboBox
        else:
            _sm = GtkTextStyle.__getOptionMenu
        _optlist = GtkTextStyle.__text_align
        _widget = _sm(_widgets, _key, _ival, _optlist)
        _idx = 0
        for _i in range(len(_optlist)):
            _val = text.TextStyle.getAlignmentFromString(_optlist[_i])
            if _val == _ival:
                _idx = _i
        _widget.set_active(_idx)
        if _key not in _widgets:
            _widgets[_key] = _widget
        #
        _key = 'TEXT_SIZE'
        _entry = _widgets.setdefault(_key, gtk.Entry())
        _ival = im.getOption(_key)
        _size = "%f" % _ival
        _entry.set_data('size', _size)
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
                                        GtkTextStyle.__entryInsertText)
            _entry.set_data('handlerid', _handlerid)
            _entry.connect('activate', GtkTextStyle.__entryActivate)
            _entry.connect('focus-out-event',
                           GtkTextStyle.__entryFocusOut)
        if _key not in _widgets:
            _widgets[_key] = _entry

def _widget_changed(widget, gts):
    if hasattr(gtk, 'ComboBox'):
        _idx = widget.get_active()
    else:
        _idx = widget.get_history()
    _textstyles = gts.getTextStyles()
    gts.setTextStyle(_textstyles[_idx])

def _fill_dialog(dvbox, gts):
    _lsg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _msg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    #
    _frame = gtk.Frame(_('Font Properties'))
    _frame.set_border_width(2)
    _vbox = gtk.VBox(False, 2)
    _vbox.set_border_width(2)
    _frame.add(_vbox)
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Family:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('FONT_FAMILY')
    _msg.add_widget(_widget)
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Style:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('FONT_STYLE')
    _msg.add_widget(_widget)
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Weight:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('FONT_WEIGHT')
    _msg.add_widget(_widget)
    _hbox.pack_start(_widget, False, False, 2)
    # 
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Alignment:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('TEXT_ALIGNMENT')
    _msg.add_widget(_widget)
    _hbox.pack_start(_widget, False, False, 2)
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, False, False, 2)
    _label = gtk.Label(_('Size:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('TEXT_SIZE')
    _hbox.pack_start(_widget, False, False, 2)
    #
    # fixme - TEXT_ANGLE
    #
    _hbox = gtk.HBox(False, 2)
    _hbox.set_border_width(2)
    _vbox.pack_start(_hbox, True, True, 2)
    _label = gtk.Label(_('Color:'))
    _lsg.add_widget(_label)
    _hbox.pack_start(_label, False, False, 2)
    _widget = gts.getWidget('FONT_COLOR')
    _hbox.pack_start(_widget, False, False, 2)
    #
    dvbox.pack_start(_frame, False, False, 2)
    
def textstyle_dialog(gtkimage, textstyles):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('TextStyle Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _ts = _image.getOption('TEXT_STYLE')
    _hbox = gtk.HBox(False, 5)
    _hbox.set_border_width(5)
    _label = gtk.Label(_('Active TextStyle:'))
    _hbox.pack_start(_label, False, False, 5)
    _idx = 0
    if hasattr(gtk, 'ComboBox'):
        _widget = gtk.combo_box_new_text()
        for _i in range(len(textstyles)):
            _textstyle = textstyles[_i]
            if (_ts is _textstyle or
                _ts == _textstyle):
                _idx = _i
            _widget.append_text(_textstyle.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(textstyles)):
            _textstyle = textstyles[_i]
            if (_ts is _textstyle or
                _ts == _textstyle):
                _idx = _i
            _item = gtk.MenuItem(_textstyle.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)

    _hbox.pack_start(_widget, False, False, 0)
    _dialog.vbox.pack_start(_hbox, True, True)
    #
    _gts = GtkTextStyle(_window)
    for _textstyle in textstyles:
        _gts.addTextStyle(_textstyle)
    _gts.setTextStyle(_ts)
    _gts.setImageSettings(_image)
    _fill_dialog(_dialog.vbox, _gts)
    _widget.connect('changed', _widget_changed, _gts)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _nts = _gts.getTextStyle()
        if _nts != _ts:
            _image.setOption('TEXT_STYLE', _nts)
        for _opt, _val in _gts.getValues():
            if _opt == 'FONT_FAMILY':
                if _val != _image.getOption(_opt):
                    _image.setOption(_opt, _val)
            elif _opt == 'FONT_STYLE':
                if _val != _image.getOption(_opt):
                    _image.setOption(_opt, _val)
            elif _opt == 'FONT_WEIGHT':
                if _val != _image.getOption(_opt):
                    _image.setOption(_opt, _val)
            elif _opt == 'FONT_COLOR':
                if _val != _image.getOption(_opt).getColors():
                    _r, _g, _b = _val
                    _image.setOption(_opt, color.Color(_r, _g, _b))
            elif _opt == 'TEXT_SIZE':
                if abs(_val - _image.getOption(_opt)) > 1e-10:
                    _image.setOption(_opt, _val)
            elif _opt == 'TEXT_ANGLE':
                if abs(_val - _image.getOption(_opt)) > 1e-10:
                    _image.setOption(_opt, _val)
            elif _opt == 'TEXT_ALIGNMENT':
                if _val != _image.getOption(_opt):
                    _image.setOption(_opt, _val)
            else:
                raise RuntimeError, "Unexpected TextStyle option '%s'" % _opt
    _gts.clear()
    _dialog.destroy()
