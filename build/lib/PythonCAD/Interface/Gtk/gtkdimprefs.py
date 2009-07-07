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
# code for displaying DimStyle values
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sys

from PythonCAD.Generic import color
from PythonCAD.Generic import units
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import image

class GtkDimStyle(object):
    """
    """
    __keys = dimension.DimStyle.getDimStyleOptions()
    __font_styles = text.TextStyle.getStyleStrings()
    __font_weights = text.TextStyle.getWeightStrings()
    __text_align = text.TextStyle.getAlignmentStrings()
    __dim_positions = dimension.Dimension.getPositionStrings()
    __dim_endpoints = dimension.Dimension.getEndpointTypeStrings()
    __units = units.Unit.getUnitStrings()
    __families = None

    def __init__(self, window, ds=None):
        if not isinstance(window, gtk.Window):
            raise TypeError, "Invalid window type: " + `type(window)`
        self.__window = window
        self.__widgets = {}
        self.__notebook = gtk.Notebook()
        self.__dimstyles = []
        self.__ds = None
        if ds is not None:
            self.setimStyle(ds)

    def getNotebook(self):
        """Get the gtk.Notebook widget in the GtkDimStyle.

getNotebook()        
        """
        return self.__notebook

    notebook = property(getNotebook, None, None, "gtk.Notebook widget")

    def addDimStyle(self, ds):
        """Store a DimStyle in the GtkDimStyle

addDimStyle(ds)

Argument 'ds' must be a DimStyle instance.
        """
        if not isinstance(ds, dimension.DimStyle):
            raise TypeError, "Invalid DimStyle: " + `type(ds)`
        self.__dimstyles.append(ds)

    def getDimStyles(self):
        """Return the list of stored DimStyles

getDimStyles()

This method returns a list of DimStyle instances stored
with the addDimStyle() method.
        """
        return self.__dimstyles

    def setDimStyle(self, ds):
        """Set the DimStyle defining the various widget values.

setDimStyle(ds)

Argument 'ds' must be a DimStyle instance.
        """
        if not isinstance(ds, dimension.DimStyle):
            raise TypeError, "Invalid DimStyle: " + `type(ds)`
        self.__ds = ds
        for _key in GtkDimStyle.__keys:
            self.setValues(_key)
        if self.__notebook.get_current_page() == -1:
            self.__initNotebook()

    def getDimStyle(self):
        """Get the DimStyle used to define the widget values.

getDimStyle()

This method returns a DimStyle instance or None if no DimStyle
has been stored in the GtkDimStyle instance.
        """
        return self.__ds

    def __getCheckButton(widgets, key, s):
        return widgets.setdefault(key, gtk.CheckButton(s))

    __getCheckButton = staticmethod(__getCheckButton)

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
            _length = entry.get_data('length')
            _hid = entry.get_data('handlerid')
            entry.delete_text(0, -1)
            entry.handler_block(_hid)
            try:
                entry.set_text(_length)
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
                    gobject.idle_add(GtkDimStyle.__moveCursor, entry)
                else:
                    gtk.idle_add(GtkDimStyle.__moveCursor, entry)
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
            _widget.connect('clicked', GtkDimStyle.__selectColor, s)
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

    def __toggleSecondaryOpts(checkbox, widgets):
        _state = checkbox.get_active()
        for _key in GtkDimStyle.__keys:
            if (_key.startswith('DIM_SECONDARY') or
                _key.startswith('RADIAL_DIM_SECONDARY') or
                _key.startswith('ANGULAR_DIM_SECONDARY')):
                _widget = widgets.get(_key)
                if _widget is not None:
                    _widget.set_sensitive(_state)

    __toggleSecondaryOpts = staticmethod(__toggleSecondaryOpts)

    def setValues(self, key):
        """Store the DimStyle values in the interface widgets.

setValues(key)
        """
        _ds = self.__ds
        if _ds is None:
            raise RuntimeError, "No DimStyle defined for the GtkDimStyle instance."
        _widgets = self.__widgets
        if (key == 'DIM_PRIMARY_FONT_FAMILY' or
            key == 'DIM_SECONDARY_FONT_FAMILY'):
            if GtkDimStyle.__families is None:
                _families = []
                _window = self.__window
                for _family in _window.get_pango_context().list_families():
                    _families.append(_family.get_name())
                _families.sort()
                GtkDimStyle.__families = _families
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__families)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_PRIMARY_FONT_STYLE' or
              key == 'DIM_SECONDARY_FONT_STYLE'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__font_styles)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_PRIMARY_FONT_WEIGHT' or
              key == 'DIM_SECONDARY_FONT_WEIGHT'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__font_weights)
            if key not in _widgets:
                _widgets[key] = _widget
        elif key == 'DIM_PRIMARY_FONT_COLOR':
            _color = _ds.getValue(key)
            _s = _('Select Primary Dimension Font Color')
            if hasattr(gtk, 'ColorButton'):
                _sm = GtkDimStyle.__getColorButton
            else:
                _sm = GtkDimStyle.__getColorDA
            _widget = _sm(_widgets, key, _color, _s)
            if key not in _widgets:
                _widgets[key] = _widget
        elif key == 'DIM_SECONDARY_FONT_COLOR':
            _color = _ds.getValue(key)
            _s = _('Select Secondary Dimension Font Color')
            if hasattr(gtk, 'ColorButton'):
                _sm = GtkDimStyle.__getColorButton
            else:
                _sm = GtkDimStyle.__getColorDA
            _widget = _sm(_widgets, key, _color, _s)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_PRIMARY_TEXT_ANGLE' or
              key == 'DIM_SECONDARY_TEXT_ANGLE'):
            pass
        elif (key == 'DIM_PRIMARY_TEXT_ALIGNMENT' or
              key == 'DIM_SECONDARY_TEXT_ALIGNMENT'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__text_align)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_PRIMARY_PREFIX' or
              key == 'DIM_SECONDARY_PREFIX' or
              key == 'DIM_PRIMARY_SUFFIX' or
              key == 'DIM_SECONDARY_SUFFIX' or
              key == 'RADIAL_DIM_PRIMARY_PREFIX' or
              key == 'RADIAL_DIM_SECONDARY_PREFIX' or
              key == 'RADIAL_DIM_PRIMARY_SUFFIX' or
              key == 'RADIAL_DIM_SECONDARY_SUFFIX' or
              key == 'ANGULAR_DIM_PRIMARY_PREFIX' or
              key == 'ANGULAR_DIM_SECONDARY_PREFIX' or
              key == 'ANGULAR_DIM_PRIMARY_SUFFIX' or
              key == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
            _entry = _widgets.setdefault(key, gtk.Entry())
            _entry.set_text(_ds.getValue(key))
            if key not in _widgets:
                _widgets[key] = _entry
        elif (key == 'DIM_PRIMARY_PRECISION' or
              key == 'DIM_SECONDARY_PRECISION'):
            _widget = _widgets.get(key)
            _val = _ds.getValue(key)
            if _widget is None:
                _adj = gtk.Adjustment(_val, 0, 15, 1, 1, 1)
                _sb = gtk.SpinButton(_adj)
                _sb.set_digits(0)
                _sb.set_numeric(True)
                _widgets[key] = _sb
            else:
                _widget.set_value(_val)
        elif (key == 'DIM_PRIMARY_UNITS' or
              key == 'DIM_SECONDARY_UNITS'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__units)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_PRIMARY_LEADING_ZERO' or
              key == 'DIM_SECONDARY_LEADING_ZERO'):
            _str = _('Print leading 0')
            _cb = GtkDimStyle.__getCheckButton(_widgets, key, _str)
            _cb.set_active(_ds.getValue(key))
            if key not in _widgets:
                _widgets[key] = _cb
        elif (key == 'DIM_PRIMARY_TRAILING_DECIMAL' or
              key == 'DIM_SECONDARY_TRAILING_DECIMAL'):
            _str = _('Print trailing decimal point')
            _cb = GtkDimStyle.__getCheckButton(_widgets, key, _str)
            _cb.set_active(_ds.getValue(key))
            if key not in _widgets:
                _widgets[key] = _cb
        elif (key == 'DIM_OFFSET' or
              key == 'DIM_EXTENSION' or
              key == 'DIM_ENDPOINT_SIZE' or
              key == 'DIM_THICKNESS' or
              key == 'DIM_PRIMARY_TEXT_SIZE' or
              key == 'DIM_SECONDARY_TEXT_SIZE'):
            _entry = _widgets.setdefault(key, gtk.Entry())
            _length = "%f" % _ds.getValue(key)
            _entry.set_data('length', _length)
            _hid = _entry.get_data('handlerid')
            if _hid is not None:
                _entry.handler_block(_hid)
                try:
                    _entry.set_text(_length)
                finally:
                    _entry.handler_unblock(_hid)
            else:
                _entry.set_text(_length)
                _handlerid = _entry.connect("insert-text",
                                            GtkDimStyle.__entryInsertText)
                _entry.set_data('handlerid', _handlerid)
                _entry.connect("activate", GtkDimStyle.__entryActivate)
                _entry.connect("focus-out-event",
                               GtkDimStyle.__entryFocusOut)
            if key not in _widgets:
                _widgets[key] = _entry
        elif (key == 'DIM_COLOR'):
            _color = _ds.getValue(key)
            _s = _('Select Dimension Color')
            if hasattr(gtk, 'ColorButton'):
                _sm = GtkDimStyle.__getColorButton
            else:
                _sm = GtkDimStyle.__getColorDA
            _widget = _sm(_widgets, key, _color, _s)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_POSITION'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__dim_positions)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_ENDPOINT'):
            _val = _ds.getValue(key)
            if hasattr(gtk, 'ComboBox'):
                _sm = GtkDimStyle.__getComboBox
            else:
                _sm = GtkDimStyle.__getOptionMenu
            _widget = _sm(_widgets, key, _val, GtkDimStyle.__dim_endpoints)
            if key not in _widgets:
                _widgets[key] = _widget
        elif (key == 'DIM_DUAL_MODE'):
            _str = _('Display secondary dimension text')
            _cb = GtkDimStyle.__getCheckButton(_widgets, key, _str)
            _cb.set_active(_ds.getValue(key))
            # _cb.connect('toggled', GtkDimStyle.__toggleSecondaryOpts, _widgets)
            if key not in _widgets:
                _widgets[key] = _cb
        elif (key == 'DIM_POSITION_OFFSET'):
            pass
        elif (key == 'DIM_DUAL_MODE_OFFSET'):
            pass
        elif (key == 'RADIAL_DIM_DIA_MODE'):
            _str = _('Show diameterical dimension value')
            _cb = GtkDimStyle.__getCheckButton(_widgets, key, _str)
            _cb.set_active(_ds.getValue(key))
            if key not in _widgets:
                _widgets[key] = _cb
        else:
            raise ValueError, "Unexpected key: " + key

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
where 'key' is the DimStyle option and 'value' is the option value.
        """
        _ds = self.__ds
        if _ds is None:
            raise RuntimeError, "No DimStyle defined for the GtkDimStyle instance."
        _values = []
        _widgets = self.__widgets
        for _key in GtkDimStyle.__keys:
            _widget = _widgets.get(_key)
            if _widget is None:
                continue
            if (_key == 'DIM_PRIMARY_FONT_FAMILY' or
                _key == 'DIM_SECONDARY_FONT_FAMILY'):
                if hasattr(gtk, 'ComboBox'):
                    _idx = _widget.get_active()
                elif isinstance(_widget, gtk.OptionMenu):
                    _idx = _widget.get_history()
                else:
                    raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
                _value = GtkDimStyle.__families[_idx]
            elif (_key == 'DIM_PRIMARY_FONT_STYLE' or
                  _key == 'DIM_SECONDARY_FONT_STYLE' or
                  _key == 'DIM_PRIMARY_FONT_WEIGHT' or
                  _key == 'DIM_SECONDARY_FONT_WEIGHT' or
                  _key == 'DIM_PRIMARY_TEXT_ALIGNMENT' or
                  _key == 'DIM_SECONDARY_TEXT_ALIGNMENT' or
                  _key == 'DIM_PRIMARY_UNITS' or
                  _key == 'DIM_SECONDARY_UNITS' or
                  _key == 'DIM_POSITION' or
                  _key == 'DIM_ENDPOINT'):
                if hasattr(gtk, 'ComboBox'):
                    _value = _widget.get_active()
                elif isinstance(_widget, gtk.OptionMenu):
                    _value = _widget.get_history()
                else:
                    raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
            elif (_key == 'DIM_PRIMARY_FONT_COLOR' or
                  _key == 'DIM_SECONDARY_FONT_COLOR' or
                  _key == 'DIM_COLOR'):
                if hasattr(gtk, 'ColorButton'):
                    _color = _widget.get_color()
                elif isinstance(_widget, gtk.Button):
                    _da = _widget.getChild().getChild()
                    _color= _da.get_style().bg[gtk.STATE_NORMAL]
                else:
                    raise TypeError, "Unexpected widget for '%s': " + (_key, `type(_widget)`)
                _value = GtkDimStyle.__getRGBValues(_color)
            elif (_key == 'DIM_PRIMARY_TEXT_ANGLE' or
                  _key == 'DIM_SECONDARY_TEXT_ANGLE'):
                pass
            elif (_key == 'DIM_PRIMARY_PREFIX' or
                  _key == 'DIM_SECONDARY_PREFIX' or
                  _key == 'DIM_PRIMARY_SUFFIX' or
                  _key == 'DIM_SECONDARY_SUFFIX' or
                  _key == 'RADIAL_DIM_PRIMARY_PREFIX' or
                  _key == 'RADIAL_DIM_SECONDARY_PREFIX' or
                  _key == 'RADIAL_DIM_PRIMARY_SUFFIX' or
                  _key == 'RADIAL_DIM_SECONDARY_SUFFIX' or
                  _key == 'ANGULAR_DIM_PRIMARY_PREFIX' or
                  _key == 'ANGULAR_DIM_SECONDARY_PREFIX' or
                  _key == 'ANGULAR_DIM_PRIMARY_SUFFIX' or
                  _key == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
                _value = _widget.get_text()
            elif (_key == 'DIM_PRIMARY_PRECISION' or
                  _key == 'DIM_SECONDARY_PRECISION'):
                _value = _widget.get_value_as_int()
            elif (_key == 'DIM_PRIMARY_LEADING_ZERO' or
                  _key == 'DIM_SECONDARY_LEADING_ZERO' or
                  _key == 'DIM_PRIMARY_TRAILING_DECIMAL' or
                  _key == 'DIM_SECONDARY_TRAILING_DECIMAL' or
                  _key == 'DIM_DUAL_MODE' or
                  _key == 'RADIAL_DIM_DIA_MODE'):
                _value = _widget.get_active()
            elif (_key == 'DIM_OFFSET' or
                  _key == 'DIM_EXTENSION' or
                  _key == 'DIM_ENDPOINT_SIZE' or
                  _key == 'DIM_THICKNESS' or
                  _key == 'DIM_PRIMARY_TEXT_SIZE' or
                  _key == 'DIM_SECONDARY_TEXT_SIZE'):
                _text = _widget.get_text()
                if len(_text) and _text != '+':
                    _value = float(_text)
                else:
                    _value = self.__ds.getOption(_key)
            elif (key == 'DIM_POSITION_OFFSET'):
                pass
            elif (key == 'DIM_DUAL_MODE_OFFSET'):
                pass
            else:
                raise ValueError, "Unexpected key: " + key
            _values.append((_key, _value))
        return _values

    def getWidget(self, key):
        """Return a widget associated with a DimStyle option.

getWidget(key)

Argument 'key' must be a valid DimStyle option key. This method
returns a widget or None.
        """
        if key not in GtkDimStyle.__keys:
            return ValueError, "Invalid DimStyle key: " + key
        return self.__widgets.get(key)

    def __generalPage(self):
        """Populate the 'General' Notebook page

__generalPage()

This method is private to the GtkDimStyle class.
        """
        _widgets = self.__widgets
        _vbox = gtk.VBox(False, 2)
        _size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        _frame = gtk.Frame(_('Dimension Bar Options'))
        _table = gtk.Table(4, 2, False)
        _table.set_border_width(2)
        _table.set_row_spacings(2)
        _table.set_col_spacings(2)
        _frame.add(_table)
        _label = gtk.Label(_('Offset length:'))
        _table.attach(_label, 0, 1, 0, 1,
                      gtk.EXPAND,
                      gtk.EXPAND,
                      2, 2)
        _widget = _widgets.get('DIM_OFFSET')
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 0, 1,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _label = gtk.Label(_('Extension length:'))
        _table.attach(_label, 0, 1, 1, 2,
                      gtk.EXPAND,
                      gtk.EXPAND,
                      2, 2)
        _widget = _widgets.get('DIM_EXTENSION')
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 1, 2,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _hbox = gtk.HBox(False, 2)
        _label = gtk.Label(_('Dimension bar color:'))
        _hbox.pack_start(_label, False, False, 2)
        _widget = _widgets.get('DIM_COLOR')
        _hbox.pack_start(_widget, False, False, 2)
        _table.attach(_hbox, 0, 2, 2, 3,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _hbox = gtk.HBox(False, 2)
        _label = gtk.Label(_('Dimension bar thickness:'))
        _hbox.pack_start(_label, False, False, 2)
        _widget = _widgets.get('DIM_THICKNESS')
        _hbox.pack_start(_widget, False, False, 2)
        _table.attach(_hbox, 0, 2, 3, 4,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _vbox.pack_start(_frame, False, False, 2)        
        #
        # options for dimension text position
        #
        _frame = gtk.Frame(_('Dimension Text Position'))
        _hbox = gtk.HBox(False, 2)
        _hbox.set_border_width(2)
        _frame.add(_hbox)
        _label = gtk.Label(_('Text Location at crossbar:'))
        _hbox.pack_start(_label, False, False, 2)
        _widget = _widgets.get('DIM_POSITION')
        _hbox.pack_start(_widget, False, False, 0)
        _vbox.pack_start(_frame, False, False, 2)
        #
        # options for dimension crossbar/crossarc markers
        #
        _frame = gtk.Frame(_('Dimension Crossbar Markers'))
        _table = gtk.Table(2, 2, False)
        _table.set_border_width(2)
        _table.set_row_spacings(2)
        _table.set_col_spacings(2)
        _frame.add(_table)
        _label = gtk.Label(_('Dimension marker:'))
        _table.attach(_label, 0, 1, 0, 1,
                      gtk.FILL,
                      gtk.FILL,
                      2, 2)
        _widget = _widgets.get('DIM_ENDPOINT')
        _table.attach(_widget, 1, 2, 0, 1,
                      gtk.FILL,
                      gtk.FILL,
                      2, 2)
        _label = gtk.Label(_('Marker size:'))
        _table.attach(_label, 0, 1, 1, 2,
                      gtk.FILL,
                      gtk.FILL,
                      2, 2)
        _widget = _widgets.get('DIM_ENDPOINT_SIZE')
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 1, 2,
                      gtk.FILL,
                      gtk.FILL,
                      2, 2)
        _vbox.pack_start(_frame, False, False, 2)
        #
        _widget = _widgets.get('DIM_DUAL_MODE')
        _vbox.pack_start(_widget, False, False, 2)     
        self.__notebook.append_page(_vbox, gtk.Label(_('General')))

    def __psPage(self, pds=True):
        """Populate the Primary/Secondary DimString pages

psPage([pds])

This method is private to the GtkDimString class.
        """
        _widgets = self.__widgets
        _vbox = gtk.VBox(False, 2)
        _frame = gtk.Frame(_('Units'))
        _frame.set_border_width(2)
        _hbox = gtk.HBox(False, 2)
        _hbox.set_border_width(2)
        _frame.add(_hbox)
        _label = gtk.Label(_('Dimension units:'))
        _hbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_UNITS'
        else:
            _key = 'DIM_SECONDARY_UNITS'
        _widget = _widgets.get(_key)
        _hbox.pack_start(_widget, False, False, 2)
        _vbox.pack_start(_frame, False, False, 2)
        #
        _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        _menu_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        #
        _frame = gtk.Frame(_('Font Properties'))
        _frame.set_border_width(2)
        _fvbox = gtk.VBox(False, 2)
        _fvbox.set_border_width(2)
        _frame.add(_fvbox)
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, False, False, 2)
        _label = gtk.Label(_('Family:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_FONT_FAMILY'
        else:
            _key = 'DIM_SECONDARY_FONT_FAMILY'
        _widget = _widgets.get(_key)
        _menu_size_group.add_widget(_widget)
        _fhbox.pack_start(_widget, False, False, 2)
        #
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, False, False, 2)
        _label = gtk.Label(_('Style:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_FONT_STYLE'
        else:
            _key = 'DIM_SECONDARY_FONT_STYLE'
        _widget = _widgets.get(_key)
        _menu_size_group.add_widget(_widget)
        _fhbox.pack_start(_widget, False, False, 2)
        #
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, False, False, 2)
        _label = gtk.Label(_('Weight:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_FONT_WEIGHT'
        else:
            _key = 'DIM_SECONDARY_FONT_WEIGHT'
        _widget = _widgets.get(_key)
        _menu_size_group.add_widget(_widget)
        _fhbox.pack_start(_widget, False, False, 2)
        # 
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, False, False, 2)
        _label = gtk.Label(_('Alignment:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_TEXT_ALIGNMENT'
        else:
            _key = 'DIM_SECONDARY_TEXT_ALIGNMENT'
        _widget = _widgets.get(_key)
        _menu_size_group.add_widget(_widget)
        _fhbox.pack_start(_widget, False, False, 2)
        #
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, False, False, 2)
        _label = gtk.Label(_('Size:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_TEXT_SIZE'
        else:
            _key = 'DIM_SECONDARY_TEXT_SIZE'
        _widget = _widgets.get(_key)
        _fhbox.pack_start(_widget, False, False, 2)
        #
        _fhbox = gtk.HBox(False, 2)
        _fhbox.set_border_width(2)
        _fvbox.pack_start(_fhbox, True, True, 2)
        _label = gtk.Label(_('Color:'))
        _label_size_group.add_widget(_label)
        _fhbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_FONT_COLOR'
        else:
            _key = 'DIM_SECONDARY_FONT_COLOR'
        _widget = _widgets.get(_key)
        _fhbox.pack_start(_widget, False, False, 2)
        _vbox.pack_start(_frame, False, False, 2)
        #
        _frame = gtk.Frame(_('Format Options'))
        _frame.set_border_width(2)
        _table = gtk.Table(3, 1, False)
        _table.set_border_width(2)
        _table.set_row_spacings(2)
        _table.set_col_spacings(2)
        _frame.add(_table)
        if pds:
            _key = 'DIM_PRIMARY_LEADING_ZERO'
        else:
            _key = 'DIM_SECONDARY_LEADING_ZERO'
        _widget = _widgets.get(_key)
        _table.attach(_widget, 0, 1, 0, 1,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        if pds:
            _key = 'DIM_PRIMARY_TRAILING_DECIMAL'
        else:
            _key = 'DIM_SECONDARY_TRAILING_DECIMAL'
        _widget = _widgets.get(_key)
        _table.attach(_widget, 0, 1, 1, 2,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        #
        _thbox = gtk.HBox(False, 2)
        _label = gtk.Label(_('Display precision:'))
        _thbox.pack_start(_label, False, False, 2)
        if pds:
            _key = 'DIM_PRIMARY_PRECISION'
        else:
            _key = 'DIM_SECONDARY_PRECISION'
        _widget = _widgets.get(_key)
        _thbox.pack_start(_widget, False, False, 2)
        _table.attach(_thbox, 0, 1, 2, 3,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _vbox.pack_start(_frame, False, False, 2)
        if pds:
            _label = gtk.Label(_('Primary'))
        else:
            _label = gtk.Label(_('Secondary'))
        self.__notebook.append_page(_vbox, _label)

    def __dimPage(self, dstr):
        """Populate the Linear/Radial/Angular dimension pages

__dimPage(dstr)

This method is private to the GtkDimStyle class
        """
        if (dstr != 'linear' and
            dstr != 'radial' and
            dstr != 'angular'):
            raise ValueError, "Unexpected argument: " + dstr
        _widgets = self.__widgets
        _vbox = gtk.VBox(False, 5)
        _size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        _frame = gtk.Frame(_('Primary Dimension Text Options'))
        _table = gtk.Table(2, 2, False)
        _table.set_border_width(5)
        _table.set_row_spacings(5)
        _table.set_col_spacings(5)
        _frame.add(_table)
        _label = gtk.Label(_('Default prefix:'))
        _table.attach(_label, 0, 1, 0, 1,
                      gtk.EXPAND,
                      gtk.EXPAND,
                      2, 2)
        if dstr == 'linear':
            _key = 'DIM_PRIMARY_PREFIX'
        elif dstr == 'radial':
            _key = 'RADIAL_DIM_PRIMARY_PREFIX'
        else:
            _key = 'ANGULAR_DIM_PRIMARY_PREFIX'
        _widget = _widgets.get(_key)
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 0, 1,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _label = gtk.Label(_('Default suffix:'))
        _table.attach(_label, 0, 1, 1, 2,
                      gtk.EXPAND,
                      gtk.EXPAND,
                      2, 2)
        if dstr == 'linear':
            _key = 'DIM_PRIMARY_SUFFIX'
        elif dstr == 'radial':
            _key = 'RADIAL_DIM_PRIMARY_SUFFIX'
        else:
            _key = 'ANGULAR_DIM_PRIMARY_SUFFIX'
        _widget = _widgets.get(_key)
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 1, 2,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _vbox.pack_start(_frame, False, False, 5)
        #
        _frame = gtk.Frame(_('Secondary Dimension Text Options'))
        _table = gtk.Table(2, 2, False)
        _table.set_border_width(5)
        _table.set_row_spacings(5)
        _table.set_col_spacings(5)
        _frame.add(_table)
        _label = gtk.Label(_('Default prefix:'))
        _table.attach(_label, 0, 1, 0, 1,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
        if dstr == 'linear':
            _key = 'DIM_SECONDARY_PREFIX'
        elif dstr == 'radial':
            _key = 'RADIAL_DIM_SECONDARY_PREFIX'
        else:
            _key = 'ANGULAR_DIM_SECONDARY_PREFIX'
        _widget = _widgets.get(_key)
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 0, 1,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _label = gtk.Label(_('Default suffix:'))
        _table.attach(_label, 0, 1, 1, 2,
                      gtk.EXPAND,
                      gtk.EXPAND,
                      2, 2)
        if dstr == 'linear':
            _key = 'DIM_SECONDARY_SUFFIX'
        elif dstr == 'radial':
            _key = 'RADIAL_DIM_SECONDARY_SUFFIX'
        else:
            _key = 'ANGULAR_DIM_SECONDARY_SUFFIX'
        _widget = _widgets.get(_key)
        _size_group.add_widget(_widget)
        _table.attach(_widget, 1, 2, 1, 2,
                      gtk.FILL | gtk.EXPAND,
                      gtk.FILL | gtk.EXPAND,
                      2, 2)
        _vbox.pack_start(_frame, False, False, 5)
        if dstr == 'radial':
            _widget = _widgets.get('RADIAL_DIM_DIA_MODE')
            _vbox.pack_start(_widget, False, False, 5)
        if dstr == 'linear':
            _label = gtk.Label(_('Linear'))
        elif dstr == 'radial':
            _label = gtk.Label(_('Radial'))
        else:
            _label = gtk.Label(_('Angular'))
        self.__notebook.append_page(_vbox, _label)

    def __initNotebook(self):
        """Populate the gtk.Notebook with widgets.

__initNotebook()

This method is private to the GtkDimStyle class.
        """
        self.__generalPage()
        self.__psPage() # Primary
        self.__psPage(False) # Secondary
        self.__dimPage('linear')
        self.__dimPage('radial')
        self.__dimPage('angular')
        
    def clear(self):
        """Clear out all values and widgets in the GtkDimStyle.

clear()        
        """
        self.__window = None
        _nb = self.__notebook
        _nb.set_current_page(0)
        while _nb.get_current_page() != -1:
            _nb.remove_page(-1)
        self.__widgets.clear()
        del self.__dimstyles[:]
        self.__ds = None

    def setImageSettings(self, im):
        """Adjust the widgets values based on current Image values

setImageSettings(im)

Argument 'im' must be an Image instance.
        """
        if not isinstance(im, image.Image):
            raise TypeError, "Invalid Image type: " + `type(im)`
        _widgets = self.__widgets
        for _key in GtkDimStyle.__keys:
            _ival = im.getOption(_key)
            if (_key == 'DIM_PRIMARY_FONT_FAMILY' or
                _key == 'DIM_SECONDARY_FONT_FAMILY'):
                if GtkDimStyle.__families is None:
                    _families = []
                    _window = self.__window
                    for _family in _window.get_pango_context().list_families():
                        _families.append(_family.get_name())
                    _families.sort()
                    GtkDimStyle.__families = _families
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _widget = _sm(_widgets, _key, _ival,
                              GtkDimStyle.__families)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_PRIMARY_FONT_STYLE' or
                  _key == 'DIM_SECONDARY_FONT_STYLE'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _optlist = GtkDimStyle.__font_styles
                _widget = _sm(_widgets, _key, _ival, _optlist)
                _idx = 0
                for _i in range(len(_optlist)):
                    _val = text.TextStyle.getStyleFromString(_optlist[_i])
                    if _val == _ival:
                        _idx = _i
                _widget.set_active(_idx)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_PRIMARY_FONT_WEIGHT' or
                  _key == 'DIM_SECONDARY_FONT_WEIGHT'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _optlist = GtkDimStyle.__font_weights
                _widget = _sm(_widgets, _key, _ival, _optlist)
                _idx = 0
                for _i in range(len(_optlist)):
                    _val = text.TextStyle.getWeightFromString(_optlist[_i])
                    if _val == _ival:
                        _idx = _i
                _widget.set_active(_idx)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif _key == 'DIM_PRIMARY_FONT_COLOR':
                _s = _('Select Primary Dimension Font Color')
                if hasattr(gtk, 'ColorButton'):
                    _sm = GtkDimStyle.__getColorButton
                else:
                    _sm = GtkDimStyle.__getColorDA
                _widget = _sm(_widgets, _key, _ival, _s)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif _key == 'DIM_SECONDARY_FONT_COLOR':
                _s = _('Select Secondary Dimension Font Color')
                if hasattr(gtk, 'ColorButton'):
                    _sm = GtkDimStyle.__getColorButton
                else:
                    _sm = GtkDimStyle.__getColorDA
                _widget = _sm(_widgets, _key, _ival, _s)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_PRIMARY_TEXT_ANGLE' or
                  _key == 'DIM_SECONDARY_TEXT_ANGLE'):
                pass
            elif (_key == 'DIM_PRIMARY_TEXT_ALIGNMENT' or
                  _key == 'DIM_SECONDARY_TEXT_ALIGNMENT'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _optlist = GtkDimStyle.__text_align
                _widget = _sm(_widgets, _key, _ival, _optlist)
                _idx = 0
                for _i in range(len(_optlist)):
                    _val = text.TextStyle.getAlignmentFromString(_optlist[_i])
                    if _val == _ival:
                        _idx = _i
                _widget.set_active(_idx)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_PRIMARY_PREFIX' or
                  _key == 'DIM_SECONDARY_PREFIX' or
                  _key == 'DIM_PRIMARY_SUFFIX' or
                  _key == 'DIM_SECONDARY_SUFFIX' or
                  _key == 'RADIAL_DIM_PRIMARY_PREFIX' or
                  _key == 'RADIAL_DIM_SECONDARY_PREFIX' or
                  _key == 'RADIAL_DIM_PRIMARY_SUFFIX' or
                  _key == 'RADIAL_DIM_SECONDARY_SUFFIX' or
                  _key == 'ANGULAR_DIM_PRIMARY_PREFIX' or
                  _key == 'ANGULAR_DIM_SECONDARY_PREFIX' or
                  _key == 'ANGULAR_DIM_PRIMARY_SUFFIX' or
                  _key == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
                _entry = _widgets.setdefault(_key, gtk.Entry())
                _entry.set_text(_ival)
                if _key not in _widgets:
                    _widgets[_key] = _entry
            elif (_key == 'DIM_PRIMARY_PRECISION' or
                  _key == 'DIM_SECONDARY_PRECISION'):
                _widget = _widgets.get(_key)
                if _widget is None:
                    _adj = gtk.Adjustment(_ival, 0, 15, 1, 1, 1)
                    _sb = gtk.SpinButton(_adj)
                    _sb.set_digits(0)
                    _sb.set_numeric(True)
                    _widgets[_key] = _sb
                else:
                    _widget.set_value(_ival)
            elif (_key == 'DIM_PRIMARY_UNITS' or
                  _key == 'DIM_SECONDARY_UNITS'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _widget = _sm(_widgets, _key, _ival, GtkDimStyle.__units)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_PRIMARY_LEADING_ZERO' or
                  _key == 'DIM_SECONDARY_LEADING_ZERO'):
                _str = _('Print leading 0')
                _cb = GtkDimStyle.__getCheckButton(_widgets, _key, _str)
                _cb.set_active(_ival)
                if _key not in _widgets:
                    _widgets[_key] = _cb
            elif (_key == 'DIM_PRIMARY_TRAILING_DECIMAL' or
                  _key == 'DIM_SECONDARY_TRAILING_DECIMAL'):
                _str = _('Print trailing decimal point')
                _cb = GtkDimStyle.__getCheckButton(_widgets, _key, _str)
                _cb.set_active(_ival)
                if _key not in _widgets:
                    _widgets[_key] = _cb
            elif (_key == 'DIM_OFFSET' or
                  _key == 'DIM_EXTENSION' or
                  _key == 'DIM_ENDPOINT_SIZE' or
                  _key == 'DIM_THICKNESS' or
                  _key == 'DIM_PRIMARY_TEXT_SIZE' or
                  _key == 'DIM_SECONDARY_TEXT_SIZE'):
                _entry = _widgets.setdefault(_key, gtk.Entry())
                _length = "%f" % _ival
                _entry.set_data('length', _length)
                _hid = _entry.get_data('handlerid')
                if _hid is not None:
                    _entry.handler_block(_hid)
                    try:
                        _entry.set_text(_length)
                    finally:
                        _entry.handler_unblock(_hid)
                else:
                    _entry.set_text(_length)
                    _handlerid = _entry.connect("insert-text",
                                                GtkDimStyle.__entryInsertText)
                    _entry.set_data('handlerid', _handlerid)
                    _entry.connect("activate", GtkDimStyle.__entryActivate)
                    _entry.connect("focus-out-event",
                                   GtkDimStyle.__entryFocusOut)
                if _key not in _widgets:
                    _widgets[_key] = _entry
            elif (_key == 'DIM_COLOR'):
                _color = _ival
                _s = _('Select Dimension Color')
                if hasattr(gtk, 'ColorButton'):
                    _sm = GtkDimStyle.__getColorButton
                else:
                    _sm = GtkDimStyle.__getColorDA
                _widget = _sm(_widgets, _key, _ival, _s)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_POSITION'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _optlist = GtkDimStyle.__dim_positions
                _widget = _sm(_widgets, _key, _ival, _optlist)
                _idx = 0
                for _i in range(len(_optlist)):
                    _val = dimension.Dimension.getPositionFromString(_optlist[_i])
                    if _val == _ival:
                        _idx = _i
                _widget.set_active(_idx)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_ENDPOINT'):
                if hasattr(gtk, 'ComboBox'):
                    _sm = GtkDimStyle.__getComboBox
                else:
                    _sm = GtkDimStyle.__getOptionMenu
                _optlist = GtkDimStyle.__dim_endpoints
                _widget = _sm(_widgets, _key, _ival, _optlist)
                _idx = 0
                for _i in range(len(_optlist)):
                    _val = dimension.Dimension.getEndpointTypeFromString(_optlist[_i])
                    if _val == _ival:
                        _idx = _i
                _widget.set_active(_idx)
                if _key not in _widgets:
                    _widgets[_key] = _widget
            elif (_key == 'DIM_DUAL_MODE'):
                _str = _('Display secondary dimension text')
                _cb = GtkDimStyle.__getCheckButton(_widgets, _key, _str)
                _cb.set_active(_ival)
                if _key not in _widgets:
                    _widgets[_key] = _cb
            elif (_key == 'DIM_POSITION_OFFSET'):
                pass
            elif (_key == 'DIM_DUAL_MODE_OFFSET'):
                pass
            elif (_key == 'RADIAL_DIM_DIA_MODE'):
                _str = _('Show diameterical dimension value')
                _cb = GtkDimStyle.__getCheckButton(_widgets, _key, _str)
                _cb.set_active(_ival)
                if _key not in _widgets:
                    _widgets[_key] = _cb
            else:
                raise ValueError, "Unexpected key: " + _key

def _widget_changed(widget, gds):
    if hasattr(gtk, 'ComboBox'):
        _idx = widget.get_active()
    else:
        _idx = widget.get_history()
    _dimstyles = gds.getDimStyles()
    gds.setDimStyle(_dimstyles[_idx])

def dimstyle_dialog(gtkimage, dimstyles):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('DimStyle Settings'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _image = gtkimage.getImage()
    _ds = _image.getOption('DIM_STYLE')
    _hbox = gtk.HBox(False, 5)
    _hbox.set_border_width(5)
    _label = gtk.Label(_('Active DimStyle:'))
    _hbox.pack_start(_label, False, False, 5)
    _idx = 0
    if hasattr(gtk, 'ComboBox'):
        _widget = gtk.combo_box_new_text()
        for _i in range(len(dimstyles)):
            _dimstyle = dimstyles[_i]
            if (_ds is _dimstyle or
                _ds == _dimstyle):
                _idx = _i
            _widget.append_text(_dimstyle.getName())
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(dimstyles)):
            _dimstyle = dimstyles[_i]
            if (_ds is _dimstyle or
                _ds == _dimstyle):
                _idx = _i
            _item = gtk.MenuItem(_dimstyle.getName())
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)

    _hbox.pack_start(_widget, False, False, 0)
    _dialog.vbox.pack_start(_hbox, True, True)
    #
    _gds = GtkDimStyle(_window)
    for _dimstyle in dimstyles:
        _gds.addDimStyle(_dimstyle)
    _gds.setDimStyle(_ds)
    _gds.setImageSettings(_image)
    _dialog.vbox.pack_start(_gds.notebook, True, True)
    _widget.connect('changed', _widget_changed, _gds)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _nds = _gds.getDimStyle()
        if _nds != _ds:
            _image.setOption('DIM_STYLE', _nds)
        for _opt, _val in _gds.getValues():
            _set = False
            _cv = _image.getOption(_opt)
            if (_opt == 'DIM_PRIMARY_FONT_FAMILY' or
                _opt == 'DIM_SECONDARY_FONT_FAMILY' or
                _opt == 'DIM_PRIMARY_FONT_WEIGHT' or
                _opt == 'DIM_SECONDARY_FONT_WEIGHT' or
                _opt == 'DIM_PRIMARY_FONT_STYLE' or
                _opt == 'DIM_SECONDARY_FONT_STYLE' or
                _opt == 'DIM_PRIMARY_TEXT_ALIGNMENT' or
                _opt == 'DIM_SECONDARY_TEXT_ALIGNMENT' or
                _opt == 'DIM_PRIMARY_PREFIX' or
                _opt == 'DIM_SECONDARY_PREFIX' or
                _opt == 'DIM_PRIMARY_SUFFIX' or
                _opt == 'DIM_SECONDARY_SUFFIX' or
                _opt == 'DIM_PRIMARY_PRECISION' or
                _opt == 'DIM_SECONDARY_PRECISION' or
                _opt == 'DIM_PRIMARY_UNITS' or
                _opt == 'DIM_SECONDARY_UNITS' or
                _opt == 'DIM_POSITION' or
                _opt == 'DIM_ENDPOINT' or
                _opt == 'RADIAL_DIM_PRIMARY_PREFIX' or
                _opt == 'RADIAL_DIM_PRIMARY_SUFFIX' or
                _opt == 'RADIAL_DIM_SECONDARY_PREFIX' or
                _opt == 'RADIAL_DIM_SECONDARY_SUFFIX' or
                _opt == 'ANGULAR_DIM_PRIMARY_PREFIX' or
                _opt == 'ANGULAR_DIM_PRIMARY_SUFFIX' or
                _opt == 'ANGULAR_DIM_SECONDARY_PREFIX' or
                _opt == 'ANGULAR_DIM_SECONDARY_SUFFIX'):
                if _val != _cv:
                    _set = True
            elif (_opt == 'DIM_PRIMARY_TEXT_SIZE' or
                  _opt == 'DIM_SECONDARY_TEXT_SIZE' or
                  _opt == 'DIM_OFFSET' or
                  _opt == 'DIM_EXTENSION' or
                  _opt == 'DIM_THICKNESS' or
                  _opt == 'DIM_ENDPOINT_SIZE'):
                if abs(_val - _cv) > 1e-10:
                    _set = True
            elif (_opt == 'DIM_PRIMARY_LEADING_ZERO' or
                  _opt == 'DIM_SECONDARY_LEADING_ZERO' or
                  _opt == 'DIM_PRIMARY_TRAILING_DECIMAL' or
                  _opt == 'DIM_SECONDARY_TRAILING_DECIMAL' or
                  _opt == 'DIM_DUAL_MODE' or
                  _opt == 'RADIAL_DIM_DIA_MODE'):
                if ((_val is False and _cv is True) or
                    (_val is True and _cv is False)):
                    _set = True
            elif (_opt == 'DIM_COLOR' or
                  _opt == 'DIM_PRIMARY_FONT_COLOR' or
                  _opt == 'DIM_SECONDARY_FONT_COLOR'):
                if _val != _cv.getColors():
                    _r, _g, _b = _val
                    _val = color.Color(_r, _g, _b)
            elif (_opt == 'DIM_PRIMARY_TEXT_ANGLE' or
                  _opt == 'DIM_SECONDARY_TEXT_ANGLE' or
                  _opt == 'DIM_POSITION_OFFSET' or
                  _opt == 'DIM_DUAL_MODE_OFFSET'):
                pass
            else:
                raise RuntimeError, "Unexpected DimStyle option: '%s'" % _opt
            if _set:
                _image.setOption(_opt, _val)
    _dialog.destroy()
    _gds.clear()
