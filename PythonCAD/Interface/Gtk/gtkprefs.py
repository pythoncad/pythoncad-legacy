#
# Copyright (c) 2002, 2003, 2004, 2006 Art Haas
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
# code for setting the preferences of an image
#

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sys

from PythonCAD.Generic import globals
from PythonCAD.Generic.text import TextStyle
from PythonCAD.Generic import units
from PythonCAD.Generic.image import Image
from PythonCAD.Generic.color import get_color
from PythonCAD.Generic import preferences
from PythonCAD.Generic.dimension import Dimension

_font_styles = TextStyle.getStyleStrings()
_font_weights = TextStyle.getWeightStrings()
_text_align = TextStyle.getAlignmentStrings()

_dim_endpoints = Dimension.getEndpointTypeStrings()
_dim_positions = Dimension.getPositionStrings()

################################################################
#
# New and improved preferences code ...
#
################################################################

class Prefstate(object):
    """A class for storing and retriving preference values.

The Prefstate class stores references to the widgets used in
making the preference dialog screens. When the dialog is closed
the widgets stored in the Prefstate class are examined for their
values if the user wants to set new preference values.

The Prefstate class has the following methods:

{set/get}TreeView(): Set/Get a gtk.TreeView for the Prefstate instance.
{set/get}HBox(): Set/Get a gtk.HBox for the Prefstate instance.
{set/get}Container(): Set/Get a reference to a gtk.Container instance.
{set/get}PrefKey(): Set/Get a key used for storing preference widget sets.
{set/get}Widget(): Set/Get a keyed reference to a widget.
hasWidgetKey(): Test if a key is used to store a widget reference.
getWidgetKeys(): Return the keys used to refer to stored widgets.
{set/get}Image(): Set/Get the Image used for preference adjustment.
{set/get}Window(): Set/Get the gtk.Window displaying the preference dialog.
{set/get}Families(): Set/Get the font families for text selection screens
clear(): Clear all storage of widgets
    """
    def __init__(self):
        self.__tree_view = None
        self.__hbox = None
        self.__prefkeys = {}
        self.__prefkey = None
        self.__widgets = {}
        self.__image = None
        self.__window = None
        self.__families = None

    def setTreeView(self, treeview):
        """Store a reference to a TreeView widget.

setTreeView(treeview)

The argument 'treeview' must be a gtk.TreeView instance.
        """
        if not isinstance(treeview, gtk.TreeView):
            raise TypeError, "Invalid TreeView: " + `type(treeview)`
        self.__tree_view = treeview

    def getTreeView(self):
        """Return the stored TreeView widget.

getTreeView()

If no gtk.TreeView has been stored this method returns None.
        """
        return self.__tree_view

    def setHBox(self, hbox):
        """Store a reference to a gtk.HBox widget.

setHBox(hbox)

The argument 'hbox' must be a gtk.HBox instance.
        """
        if not isinstance(hbox, gtk.HBox):
            raise TypeError, "Invalid HBox: " + `type(hbox)`
        self.__hbox = hbox

    def getHBox(self):
        """Return the stored gtk.HBox.

getHBox()

If no gtk.HBox has been stored this method returns None.
        """
        return self.__hbox

    def setContainer(self, key, container):
        """Store a keyed reference to a gtk.Container instance.

setContainer(key, container)

Argument 'key' is a text string, and the container must be
an instance of gtk.Container.
        """
        if not isinstance(container, gtk.Container):
            raise TypeError, "Invalid container: " + `type(container)`
        self.__prefkeys[key] = container

    def getContainer(self, key):
        """Retrieve the gtk.Container referenced by a key.

getContainer(key)

If the key has been used to store a gtk.Container instance, the
stored container is returned. If not, None is returned.
        """
        if key in self.__prefkeys:
            _container = self.__prefkeys[key]
        else:
            _container = None
        return _container

    def setPrefKey(self, key):
        """Store a key representing a screenful of preference widgets.

setPrefKey(key)

Argument 'key' should be a string.
        """
        if key not in self.__prefkeys:
            raise ValueError, "No container stored for key."
        self.__prefkey = key

    def getPrefKey(self):
        """Return the current key giving the preference widget screen.

getPrefKey()

This method returns the key last set by setPrefKey(). If that method
has not been invoked None is returned.
        """
        return self.__prefkey

    def delPrefKey(self):
        self.__prefkey = None

    def setWidget(self, key, widget):
        """Store a widget reference in the Prefstate.

setWidget(key, widget)

Argument 'key' should be a string. Argument 'widget' must be an
instance of gtk.Widget. Trying to use the same key twice will
raise a ValueError exception.
        """
        if not isinstance(widget, gtk.Widget):
            raise TypeError, "Invalid widget: " + `type(widget)`
        if key in self.__widgets:
            raise ValueError, "Duplicate key: " + key
        self.__widgets[key] = widget

    def getWidget(self, key):
        """Return the widget associated with a key

getWidget(key)

Argument 'key' should be a string. Using a key that has not
been used with setWidget() results in a KeyError exception.
        """
        return self.__widgets[key]

    def hasWidgetKey(self, key):
        """Test if a key is used for widget association.

hasWidgetKey(key)

This method returns True if the key has already been used to
store a widget.
        """
        return key in self.__widgets

    def getWidgetKeys(self):
        """Return all the keys used to store widgets.

getWidgetKeys()

This method returns a list of strings.
        """
        return self.__widgets.keys()

    def setImage(self, image):
        """Store a reference to the image used for preference adjustment.

setImage(image)

Argument 'image' must be an instance of image.Image.
        """
        if not isinstance(image, Image):
            raise TypeError, "Invalid image: " + `type(image)`
        self.__image = image

    def getImage(self):
        """Retrieve the image used for this Prefstate instance.

getImage()

This method raises a ValueError exception if it is called before
setImage().
        """
        if self.__image is None:
            raise ValueError, "Image not set."
        return self.__image

    def setWindow(self, window):
        """Store a reference to a gtk.Window.

setWindow(window)

Argument 'window' must be an instance of gtk.Window.
        """
        if not isinstance(window, gtk.Window):
            raise TypeError, "Invalid window: " + `type(window)`
        self.__window = window

    def getWindow(self):
        """Return the stored window for the Prefstate instance.

getWindow()

This method raises a ValueError exception if it is invoked before
setWindow() has been called.
        """
        if self.__window is None:
            raise ValueError, "Window not set."
        return self.__window

    def setFamilies(self, families):
        """Store a list of font families.

setFamilies(families)

Argument 'families' should be a list.
        """
        if not isinstance(families, list):
            raise TypeError, "Invalid families list: " + `type(families)`
        self.__families = families

    def getFamilies(self):
        """Return the list of families stored in the Prefstate instance.

getFamilies()

If setFamilies() has not been called, this method returns None
        """
        return self.__families

    def clear(self):
        """Release all widget references.

clear()

This method should only be called once the usage of a Prefstate
instance is completed.
        """
        self.__tree_view = None
        self.__hbox = None
        self.__prefkeys.clear()
        self.__prefkey = None
        self.__widgets.clear()
        self.__image = None
        self.__window = None
        self.__families = None
    
def entry_activate(entry):
    _text = entry.get_text()
    entry.delete_text(0, -1)
    if len(_text):
        if _text == '-' or _text == '+':
            sys.stderr.write("Incomplete value: '%s'\n" % _text)
        else:
            try:
                _value = float(_text)
                print "value: %g" % _value
            except:
                sys.stderr.write("Invalid float: '%s'\n" % _text)
    else:
        sys.stderr.write("Empty entry box.")

#
# use focus-out events to reset the value in entry boxes
# to their previous value if the entry box text is invalid
#

def _leader_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['LEADER_ARROW_SIZE']
        entry.set_text(_size)
    return False

def _dim_offset_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['DIM_OFFSET']
        entry.set_text(_size)
    return False

def _dim_marker_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['DIM_ENDPOINT_SIZE']
        entry.set_text(_size)
    return False

def _dim_extlen_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['DIM_EXTENSION']
        entry.set_text(_size)
    return False

def _thickness_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['LINE_THICKNESS']
        entry.set_text(_size)
    return False

def _chamfer_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['CHAMFER_LENGTH']
        entry.set_text(_size)
    return False

def _fillet_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['FILLET_RADIUS']
        entry.set_text(_size)
    return False

def _textsize_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['TEXT_SIZE']
        entry.set_text(_size)
    return False

def _dim_primary_textsize_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['DIM_PRIMARY_TEXT_SIZE']
        entry.set_text(_size)
    return False

def _dim_secondary_textsize_entry_focus_out(entry, event, prefstate):
    _text = entry.get_text()
    if _text == '' or _text == '+':
        entry.delete_text(0, -1)
        _size = "%f" % globals.prefs['DIM_SECONDARY_TEXT_SIZE']
        entry.set_text(_size)
    return False

def entry_focus_out(entry, event):
    _text = entry.get_text()
    if _text == '-' or _text == '+':
        entry.delete_text(0, -1)
    return False

#
# color change button handlers
#

def _get_rgb_values(color):
    if not isinstance(color, gtk.gdk.Color):
        raise TypeError, "Unexpected color type: " + `type(color)`
    _r = int(round((color.red/65535.0) * 255.0))
    _g = int(round((color.green/65535.0) * 255.0))
    _b = int(round((color.blue/65535.0) * 255.0))
    return _r, _g, _b

def _select_background_color(button):
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_('Choose New Color'))
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

def _select_dimbar_color(button):
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_('Set Dimension Bar Color'))
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

def _select_font_color(button):
    _da = button.get_child().get_child()
    _color = _da.get_style().bg[gtk.STATE_NORMAL]
    _dialog = gtk.ColorSelectionDialog(_('Set Font Color'))
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

#

def _toggle_widgets_on(widget, checkbox):
    if widget is not checkbox:
        widget.set_sensitive(True)

def _toggle_widgets_off(widget, checkbox):
    if widget is not checkbox:
        widget.set_sensitive(False)

def _toggle_secondary_dim_opts(checkbox, vbox):
    if checkbox.get_active():
        vbox.foreach(_toggle_widgets_on, checkbox)
    else:
        vbox.foreach(_toggle_widgets_off, checkbox)

def move_cursor(entry):
    entry.set_position(-1)
    return False

def entry_insert_text(entry, new_text, new_text_length, position):
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
                    _pos = entry.insert_text(new_text, _pos)
                except StandardError, e:
                    _move = False
                    sys.stdout.write("exception: '%s'\n" % e)
        finally:
            entry.handler_unblock(_hid)
        if _move:
            if hasattr(gobject, 'idle_add'):
                gobject.idle_add(move_cursor, entry)
            else:
                gtk.idle_add(move_cursor, entry)
    entry.stop_emission("insert-text")

def tree_select_cb(selection, prefstate):
    if selection is not None:
        _model, _iter = selection.get_selected()
        if _iter is not None:
            _hbox = prefstate.getHBox()
            _prefkey = prefstate.getPrefKey()
            if _prefkey is not None:
                _old_container = prefstate.getContainer(_prefkey)
                assert _old_container is not None, "No container: " + _prefkey
            _pstring = _model.get_value(_iter, 1)
            # print "second field: '%s'" % _pstring
            _new_container = prefstate.getContainer(_pstring)
            if _new_container is None:
                if _pstring == 'dimensions':
                    _new_container = _make_dimension_opts(prefstate)
                elif _pstring == 'linear':
                    _new_container = _make_linear_opts(prefstate)
                elif _pstring == 'radial':
                    _new_container = _make_radial_opts(prefstate)
                elif _pstring == 'angular':
                    _new_container = _make_angular_opts(prefstate)
                elif _pstring == 'basic':
                    _new_container = _make_basic_opts(prefstate)
                elif _pstring == 'sizes':
                    _new_container = _make_size_opts(prefstate)
                elif _pstring == 'chamfers':
                    _new_container = None
                elif _pstring == 'fillets':
                    _new_container = None
                elif _pstring == 'text':
                    _new_container = _make_text_opts(prefstate)
                elif _pstring == 'primary':
                    _new_container = _make_primary_opts(prefstate)
                elif _pstring == 'secondary':
                    _new_container = _make_secondary_opts(prefstate)
                else:
                    print "unexpected string: '%s'" % _pstring
            if _new_container is not None:
                _frame = None
                if _pstring == 'linear':
                    _frame = prefstate.getWidget('LINEAR_SECONDARY_FRAME')
                elif _pstring == 'radial':
                    _frame = prefstate.getWidget('RADIAL_SECONDARY_FRAME')
                elif _pstring == 'angular':
                    _frame = prefstate.getWidget('ANGULAR_SECONDARY_FRAME')
                else:
                    pass
                if _frame is not None:
                    _flag = True
                    if prefstate.hasWidgetKey('DIM_DUAL_MODE'):
                        _cb = prefstate.getWidget('DIM_DUAL_MODE')
                        _flag = _cb.get_active()
                    if _flag:
                        _frame.foreach(_toggle_widgets_on, _frame)
                    else:
                        _frame.foreach(_toggle_widgets_off, _frame)
                if _prefkey is not None:
                    _old_container.hide_all()
                    _hbox.remove(_old_container)
                _new_container.show_all()
                prefstate.setContainer(_pstring, _new_container)
                prefstate.setPrefKey(_pstring)
                _hbox.pack_start(_new_container, True, True, 5)
                #
                # the second time a new container is shown it may not
                # redraw completely - why?
                #
                _hbox.show_all()

def _make_dimension_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)
    _text = "<span weight='bold' size='16000'>%s</span>" % _('General Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

    _size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    #
    # options for dimension bars
    #
    _frame = gtk.Frame(_('Dimension Bar Options'))
    _table = gtk.Table(5, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    _label = gtk.Label(_('Offset length:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _length = "%f" % globals.prefs['DIM_OFFSET']
    _entry.set_text(_length)
    if not prefstate.hasWidgetKey('DIM_OFFSET'):
        prefstate.setWidget('DIM_OFFSET', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _dim_offset_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _size_group.add_widget(_entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _thbox = gtk.HBox(False)
    _thbox.set_border_width(2)
    _label = gtk.Label(_('The offset length is the distance between the dimension point and the start of the dimension bar.'))
    _thbox.pack_start(_label, False, False)
    _label.set_line_wrap(True)
    _table.attach(_thbox, 0, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    #
    _label = gtk.Label(_('Extension length:'))
    _table.attach(_label, 0, 1, 2, 3,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _length = "%f" % globals.prefs['DIM_EXTENSION']
    _entry.set_text(_length)
    if not prefstate.hasWidgetKey('DIM_EXTENSION'):
        prefstate.setWidget('DIM_EXTENSION', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _dim_extlen_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _size_group.add_widget(_entry)
    _table.attach(_entry, 1, 2, 2, 3,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _thbox = gtk.HBox(False)
    _thbox.set_border_width(2)
    _label = gtk.Label(_('The extension length is the distance the dimension bars extend beyond the dimension crossbar/crossarc.'))
    _label.set_line_wrap(True)
    _thbox.pack_start(_label, False, False)
    _table.attach(_thbox, 0, 2, 3, 4,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _fhbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('Dimension bar color:'))
    _fhbox.pack_start(_label, False, False, 5)
    _color = globals.prefs['DIM_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Dimension Color'))
        if not prefstate.hasWidgetKey('DIM_COLOR'):
            prefstate.setWidget('DIM_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('DIM_COLOR'):
            prefstate.setWidget('DIM_COLOR', _da)
        _button.connect("clicked", _select_dimbar_color)
        _bframe.add(_da)
    _fhbox.pack_start(_button, False, False, 5)
    _table.attach(_fhbox, 0, 2, 4, 5,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    #
    # options for dimension text position
    #
    _frame = gtk.Frame(_('Dimension Text Position'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Text Location at crossbar:'))
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _cur_pos = globals.prefs['DIM_POSITION']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_dim_positions)):
            _name = _dim_positions[_i]
            if _cur_pos == Dimension.getPositionFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_dim_positions)):
            _name = _dim_positions[_i]
            if _cur_pos == Dimension.getPositionFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_POSITION'):
        prefstate.setWidget('DIM_POSITION', _widget)
    _fhbox.pack_start(_widget, False, False, 0)
    _vbox.pack_start(_frame, False, False, 5)
    #
    # options for dimension crossbar/crossarc markers
    #
    _frame = gtk.Frame(_('Dimension Crossbar Markers'))
    _table = gtk.Table(2, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    _label = gtk.Label(_('Dimension marker:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)

    _idx = 0
    _endpt = globals.prefs['DIM_ENDPOINT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_dim_endpoints)):
            _name = _dim_endpoints[_i]
            if _endpt == Dimension.getEndpointTypeFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_dim_endpoints)):
            _name = _dim_endpoints[_i]
            if _endpt == Dimension.getEndpointTypeFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_ENDPOINT'):
        prefstate.setWidget('DIM_ENDPOINT', _widget)
    _table.attach(_widget, 1, 2, 0, 1,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    #
    _label = gtk.Label(_('Marker size:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _entry = gtk.Entry()
    _size = "%f" % globals.prefs['DIM_ENDPOINT_SIZE']
    _entry.set_text(_size)
    if not prefstate.hasWidgetKey('DIM_ENDPOINT_SIZE'):
        prefstate.setWidget('DIM_ENDPOINT_SIZE', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _dim_marker_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _size_group.add_widget(_entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_primary_opts(prefstate):
    _vbox = gtk.VBox(False, 2)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)
    _text = "<span weight='bold' size='16000'>%s</span>" % _('Primary Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Units'))
    _frame.set_border_width(2)
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(2)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Primary dimension units:'))
    _fhbox.pack_start(_label, False, False, 5)

    _idx = 0
    _units = units.get_all_units()
    _cur_unit = globals.prefs['DIM_PRIMARY_UNITS']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_units)):
            if _i == _cur_unit:
                _idx = _i
            _widget.append_text(_units[_i])
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_units)):
            if _i == _cur_unit:
                _idx = _i
            _item = gtk.MenuItem(_units[_i])
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_UNITS'):
        prefstate.setWidget('DIM_PRIMARY_UNITS', _widget)
    _fhbox.pack_start(_widget, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _menu_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    #
    _frame = gtk.Frame(_('Font Properties'))
    _frame.set_border_width(2)
    _fvbox = gtk.VBox(False, 5)
    _fvbox.set_border_width(2)
    _frame.add(_fvbox)
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Family:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _families = prefstate.getFamilies()
    if _families is None:
        _families = []
        _window = prefstate.getWindow()        
        for _family in _window.get_pango_context().list_families():
            _families.append(_family.get_name())
        _families.sort()
        prefstate.setFamilies(_families)

    _idx = 0
    _family = globals.prefs['DIM_PRIMARY_FONT_FAMILY']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _widget.append_text(_f)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _item = gtk.MenuItem(_f)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_FONT_FAMILY'):
        prefstate.setWidget('DIM_PRIMARY_FONT_FAMILY', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Style:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)

    _idx = 0
    _style = globals.prefs['DIM_PRIMARY_FONT_STYLE']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_styles)):
            _name = _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_font_styles)):
            _name = _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_FONT_STYLE'):
        prefstate.setWidget('DIM_PRIMARY_FONT_STYLE', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Weight:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _weight = globals.prefs['DIM_PRIMARY_FONT_WEIGHT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_weights)):
            _name = _font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_font_weights)):
            _name =_font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_FONT_WEIGHT'):
        prefstate.setWidget('DIM_PRIMARY_FONT_WEIGHT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Alignment:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _align = globals.prefs['DIM_PRIMARY_TEXT_ALIGNMENT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_text_align)):
            _name = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_text_align)):
            _name  = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_TEXT_ALIGNMENT'):
        prefstate.setWidget('DIM_PRIMARY_TEXT_ALIGNMENT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Size:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _size = "%f" % globals.prefs['DIM_PRIMARY_TEXT_SIZE']
    _entry.set_text(_size)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_TEXT_SIZE'):
        prefstate.setWidget('DIM_PRIMARY_TEXT_SIZE', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event",
                   _dim_primary_textsize_entry_focus_out,
                   prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    # _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(2)
    _label = gtk.Label(_('Color:'))
    _fhbox.pack_start(_label, False, False, 5)
    _color = globals.prefs['DIM_PRIMARY_FONT_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Primary Dimension Font Color'))
        if not prefstate.hasWidgetKey('DIM_PRIMARY_FONT_COLOR'):
            prefstate.setWidget('DIM_PRIMARY_FONT_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('DIM_PRIMARY_FONT_COLOR'):
            prefstate.setWidget('DIM_PRIMARY_FONT_COLOR', _da)
        _button.connect("clicked", _select_font_color)
        _bframe.add(_da)
    _fhbox.pack_start(_button, False, False, 5)
    _fvbox.pack_start(_fhbox, True, True, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    _frame = gtk.Frame(_('Format Options'))
    _frame.set_border_width(2)
    _table = gtk.Table(3, 1, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    _cb = gtk.CheckButton(_('Print leading 0'))
    _state = globals.prefs['DIM_PRIMARY_LEADING_ZERO']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_LEADING_ZERO'):
        prefstate.setWidget('DIM_PRIMARY_LEADING_ZERO', _cb)
    _table.attach(_cb, 0, 1, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)

    _cb = gtk.CheckButton(_('Print trailing decimal point'))
    _state = globals.prefs['DIM_PRIMARY_TRAILING_DECIMAL']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_TRAILING_DECIMAL'):
        prefstate.setWidget('DIM_PRIMARY_TRAILING_DECIMAL', _cb)
    _table.attach(_cb, 0, 1, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)

    _thbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('Display precision:'))
    _thbox.pack_start(_label, False, False, 5)
    _prec = globals.prefs['DIM_PRIMARY_PRECISION']
    _adj = gtk.Adjustment(_prec, 0, 15, 1, 1, 1)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(0)
    _sb.set_numeric(True)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_PRECISION'):
        prefstate.setWidget('DIM_PRIMARY_PRECISION', _sb)
    _thbox.pack_start(_sb, False, False, 5)
    _table.attach(_thbox, 0, 1, 2, 3,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_secondary_opts(prefstate):
    _vbox = gtk.VBox(False, 2)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)
    _text = "<span weight='bold' size='16000'>%s</span>" % _('Secondary Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, True, True, 5)
    #
    # it would be good to allow the widgets to be used if
    # the check box is active ...
    #
    _cb = gtk.CheckButton(_('Display secondary dimension text'))
    _state = globals.prefs['DIM_DUAL_MODE']
    _cb.set_active(_state)
    _cb.connect("toggled", _toggle_secondary_dim_opts, _vbox)
    if not prefstate.hasWidgetKey('DIM_DUAL_MODE'):
        prefstate.setWidget('DIM_DUAL_MODE', _cb)
    _vbox.pack_start(_cb, False, False, 5)

    _frame = gtk.Frame(_('Units'))
    _frame.set_border_width(2)
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(2)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Secondary dimension units:'))
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _units = units.get_all_units()
    _cur_unit = globals.prefs['DIM_SECONDARY_UNITS']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_units)):
            if _i == _cur_unit:
                _idx = _i
            _widget.append_text(_units[_i])
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_units)):
            if _i == _cur_unit:
                _idx = _i
            _item = gtk.MenuItem(_units[_i])
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_UNITS'):
        prefstate.setWidget('DIM_SECONDARY_UNITS', _widget)
    _fhbox.pack_start(_widget, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _menu_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    #
    _frame = gtk.Frame(_('Font Properties'))
    _frame.set_border_width(2)
    _fvbox = gtk.VBox(False, 5)
    _fvbox.set_border_width(2)
    _frame.add(_fvbox)
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Family:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _families = prefstate.getFamilies()
    if _families is None:
        _families = []
        _window = prefstate.getWindow()        
        for _family in _window.get_pango_context().list_families():
            _families.append(_family.get_name())
        _families.sort()
        prefstate.setFamilies(_families)
    _idx = 0
    _family = globals.prefs['DIM_SECONDARY_FONT_FAMILY']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _widget.append_text(_f)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _item = gtk.MenuItem(_f)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_FONT_FAMILY'):
        prefstate.setWidget('DIM_SECONDARY_FONT_FAMILY', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Style:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _style = globals.prefs['DIM_SECONDARY_FONT_STYLE']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_styles)):
            _name = _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_font_styles)):
            _name =  _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_FONT_STYLE'):
        prefstate.setWidget('DIM_SECONDARY_FONT_STYLE', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Weight:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _weight = globals.prefs['DIM_SECONDARY_FONT_WEIGHT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_weights)):
            _name = _font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_font_weights)):
            _name = _font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_FONT_WEIGHT'):
        prefstate.setWidget('DIM_SECONDARY_FONT_WEIGHT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Alignment:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _align = globals.prefs['DIM_SECONDARY_TEXT_ALIGNMENT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_text_align)):
            _name = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_text_align)):
            _name = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_TEXT_ALIGNMENT'):
        prefstate.setWidget('DIM_SECONDARY_TEXT_ALIGNMENT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Size:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _size = "%f" % globals.prefs['DIM_SECONDARY_TEXT_SIZE']
    _entry.set_text(_size)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_TEXT_SIZE'):
        prefstate.setWidget('DIM_SECONDARY_TEXT_SIZE', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event",
                   _dim_secondary_textsize_entry_focus_out,
                   prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    # _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(2)
    _label = gtk.Label(_('Color:'))
    _fhbox.pack_start(_label, False, False, 5)
    _color = globals.prefs['DIM_SECONDARY_FONT_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Secondary Dimension Font Color'))
        if not prefstate.hasWidgetKey('DIM_SECONDARY_FONT_COLOR'):
            prefstate.setWidget('DIM_SECONDARY_FONT_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('DIM_SECONDARY_FONT_COLOR'):
            prefstate.setWidget('DIM_SECONDARY_FONT_COLOR', _da)
        _button.connect("clicked", _select_font_color)
        _bframe.add(_da)
    _fhbox.pack_start(_button, False, False, 5)
    _fvbox.pack_start(_fhbox, True, True, 5)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Format Options'))
    _frame.set_border_width(2)
    _table = gtk.Table(3, 1, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    _cb = gtk.CheckButton(_('Print leading 0'))
    _state = globals.prefs['DIM_SECONDARY_LEADING_ZERO']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_LEADING_ZERO'):
        prefstate.setWidget('DIM_SECONDARY_LEADING_ZERO', _cb)
    _table.attach(_cb, 0, 1, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)

    _cb = gtk.CheckButton(_('Print trailing decimal point'))
    _state = globals.prefs['DIM_SECONDARY_TRAILING_DECIMAL']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_TRAILING_DECIMAL'):
        prefstate.setWidget('DIM_SECONDARY_TRAILING_DECIMAL', _cb)
    _table.attach(_cb, 0, 1, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)

    _thbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('Display precision:'))
    _thbox.pack_start(_label, False, False, 5)
    _prec = globals.prefs['DIM_SECONDARY_PRECISION']
    _adj = gtk.Adjustment(_prec, 0, 15, 1, 1, 1)
    _sb = gtk.SpinButton(_adj)
    _sb.set_digits(0)
    _sb.set_numeric(True)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_PRECISION'):
        prefstate.setWidget('DIM_SECONDARY_PRECISION', _sb)
    _thbox.pack_start(_sb, False, False, 5)
    _table.attach(_thbox, 0, 1, 2, 3,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    _cb = prefstate.getWidget('DIM_DUAL_MODE')
    _cb.emit("toggled")
    return _vbox

def _make_linear_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Linear Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

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
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['DIM_PRIMARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_PREFIX'):
        prefstate.setWidget('DIM_PRIMARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['DIM_PRIMARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('DIM_PRIMARY_SUFFIX'):
        prefstate.setWidget('DIM_PRIMARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Secondary Dimension Text Options'))
    _table = gtk.Table(2, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    if not prefstate.hasWidgetKey('LINEAR_SECONDARY_FRAME'):
        prefstate.setWidget('LINEAR_SECONDARY_FRAME', _frame)
    _label = gtk.Label(_('Default prefix:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['DIM_SECONDARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_PREFIX'):
        prefstate.setWidget('DIM_SECONDARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['DIM_SECONDARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('DIM_SECONDARY_SUFFIX'):
        prefstate.setWidget('DIM_SECONDARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_radial_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Radial Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

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
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['RADIAL_DIM_PRIMARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('RADIAL_DIM_PRIMARY_PREFIX'):
        prefstate.setWidget('RADIAL_DIM_PRIMARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['RADIAL_DIM_PRIMARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('RADIAL_DIM_PRIMARY_SUFFIX'):
        prefstate.setWidget('RADIAL_DIM_PRIMARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Secondary Dimension Text Options'))
    _table = gtk.Table(2, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    if not prefstate.hasWidgetKey('RADIAL_SECONDARY_FRAME'):
        prefstate.setWidget('RADIAL_SECONDARY_FRAME', _frame)
    _label = gtk.Label(_('Default prefix:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['RADIAL_DIM_SECONDARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('RADIAL_DIM_SECONDARY_PREFIX'):
        prefstate.setWidget('RADIAL_DIM_SECONDARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['RADIAL_DIM_SECONDARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('RADIAL_DIM_SECONDARY_SUFFIX'):
        prefstate.setWidget('RADIAL_DIM_SECONDARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)

    _cb = gtk.CheckButton(_('Show diametrical dimension value'))
    _state = globals.prefs['RADIAL_DIM_DIA_MODE']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('RADIAL_DIM_DIA_MODE'):
        prefstate.setWidget('RADIAL_DIM_DIA_MODE', _cb)
    _vbox.pack_start(_cb, False, False, 5)
    return _vbox

def _make_angular_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Angular Dimension Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

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
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['ANGULAR_DIM_PRIMARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('ANGULAR_DIM_PRIMARY_PREFIX'):
        prefstate.setWidget('ANGULAR_DIM_PRIMARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['ANGULAR_DIM_PRIMARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('ANGULAR_DIM_PRIMARY_SUFFIX'):
        prefstate.setWidget('ANGULAR_DIM_PRIMARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Secondary Dimension Text Options'))
    _table = gtk.Table(2, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    if not prefstate.hasWidgetKey('ANGULAR_SECONDARY_FRAME'):
        prefstate.setWidget('ANGULAR_SECONDARY_FRAME', _frame)
    _label = gtk.Label(_('Default prefix:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['ANGULAR_DIM_SECONDARY_PREFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('ANGULAR_DIM_SECONDARY_PREFIX'):
        prefstate.setWidget('ANGULAR_DIM_SECONDARY_PREFIX', _entry)
    _table.attach(_entry, 1, 2, 0, 1,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _label = gtk.Label(_('Default suffix:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.EXPAND,
                  gtk.EXPAND,
                  2, 2)
    _entry = gtk.Entry()
    _entry.set_text(globals.prefs['ANGULAR_DIM_SECONDARY_SUFFIX'])
    _size_group.add_widget(_entry)
    if not prefstate.hasWidgetKey('ANGULAR_DIM_SECONDARY_SUFFIX'):
        prefstate.setWidget('ANGULAR_DIM_SECONDARY_SUFFIX', _entry)
    _table.attach(_entry, 1, 2, 1, 2,
                  gtk.FILL | gtk.EXPAND,
                  gtk.FILL | gtk.EXPAND,
                  2, 2)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_basic_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Basic Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Units'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Drawing units:'))
    _fhbox.pack_start(_label, False, False, 5)
    _unit_list = units.get_all_units()
    _cur_unit = globals.prefs['UNITS']
    _idx = 0
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_unit_list)):
            if _i == _cur_unit:
                _idx = _i
            _widget.append_text(_unit_list[_i])
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_unit_list)):
            if _i == _cur_unit:
                _idx = _i
            _item = gtk.MenuItem(_unit_list[_i])
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('DRAWING_UNITS'):
        prefstate.setWidget('DRAWING_UNITS', _widget)
    _fhbox.pack_start(_widget, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Highlight Points'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _cb = gtk.CheckButton(_('Boxes are drawn around Point objects'))
    _state = globals.prefs['HIGHLIGHT_POINTS']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('HIGHLIGHT_POINTS'):
        prefstate.setWidget('HIGHLIGHT_POINTS', _cb)
    _fhbox.pack_start(_cb, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Autosplitting'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _cb = gtk.CheckButton(_('New Points split existing entities'))
    _state = globals.prefs['AUTOSPLIT']
    _cb.set_active(_state)
    if not prefstate.hasWidgetKey('AUTOSPLIT'):
        prefstate.setWidget('AUTOSPLIT', _cb)
    _fhbox.pack_start(_cb, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)

    _frame = gtk.Frame(_('Colors'))
    _table = gtk.Table(4, 2, False)
    _table.set_border_width(5)
    _table.set_row_spacings(5)
    _table.set_col_spacings(5)
    _frame.add(_table)
    _label = gtk.Label(_('Drawing area color:'))
    _table.attach(_label, 0, 1, 0, 1,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _color = globals.prefs['BACKGROUND_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Background Color'))
        if not prefstate.hasWidgetKey('BACKGROUND_COLOR'):
            prefstate.setWidget('BACKGROUND_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('BACKGROUND_COLOR'):
            prefstate.setWidget('BACKGROUND_COLOR', _da)
            _bframe.add(_da)
        _button.connect("clicked", _select_background_color)
    _table.attach(_button, 1, 2, 0, 1,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    #
    _label = gtk.Label(_('Inactive layer color:'))
    _table.attach(_label, 0, 1, 1, 2,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _color = globals.prefs['INACTIVE_LAYER_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Inactive Layer Color'))
        if not prefstate.hasWidgetKey('INACTIVE_LAYER_COLOR'):
            prefstate.setWidget('INACTIVE_LAYER_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('INACTIVE_LAYER_COLOR'):
            prefstate.setWidget('INACTIVE_LAYER_COLOR', _da)
        _bframe.add(_da)
        _button.connect("clicked", _select_background_color)
    _table.attach(_button, 1, 2, 1, 2,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    #
    _label = gtk.Label(_('Single point color:'))
    _table.attach(_label, 0, 1, 2, 3,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _color = globals.prefs['SINGLE_POINT_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Single Use Point Outline Color'))
        if not prefstate.hasWidgetKey('SINGLE_POINT_COLOR'):
            prefstate.setWidget('SINGLE_POINT_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('SINGLE_POINT_COLOR'):
            prefstate.setWidget('SINGLE_POINT_COLOR', _da)
        _bframe.add(_da)
        _button.connect("clicked", _select_background_color)
    _table.attach(_button, 1, 2, 2, 3,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    #
    _label = gtk.Label(_('Multi point color:'))
    _table.attach(_label, 0, 1, 3, 4,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    _color = globals.prefs['MULTI_POINT_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Multi-Use Point Outline Color'))
        if not prefstate.hasWidgetKey('MULTI_POINT_COLOR'):
            prefstate.setWidget('MULTI_POINT_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('MULTI_POINT_COLOR'):
            prefstate.setWidget('MULTI_POINT_COLOR', _da)
        _bframe.add(_da)
        _button.connect("clicked", _select_background_color)
    _table.attach(_button, 1, 2, 3, 4,
                  gtk.FILL,
                  gtk.FILL,
                  2, 2)
    
    _vbox.pack_start(_frame, False, False, 5)
    _size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

    _frame = gtk.Frame(_('Line Thickness'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Thickness:'))
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _thickness = "%f" % globals.prefs['LINE_THICKNESS']
    _entry.set_text(_thickness)
    if not prefstate.hasWidgetKey('LINE_THICKNESS'):
        prefstate.setWidget('LINE_THICKNESS', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _thickness_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_size_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _entry_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Size Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)
    #
    # leader line arrow size
    #
    _frame = gtk.Frame(_('Leader Arrow Size'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)
    _label = gtk.Label(_('Size:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _arrowsize = "%f" % globals.prefs['LEADER_ARROW_SIZE']
    _entry.set_text(_arrowsize)
    if not prefstate.hasWidgetKey('LEADER_ARROW_SIZE'):
        prefstate.setWidget('LEADER_ARROW_SIZE', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _leader_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    # Chamfer length
    #
    _frame = gtk.Frame(_('Chamfer Length'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)

    _label = gtk.Label(_('Length:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _length = "%f" % globals.prefs['CHAMFER_LENGTH']
    _entry.set_text(_length)
    if not prefstate.hasWidgetKey('CHAMFER_LENGTH'):
        prefstate.setWidget('CHAMFER_LENGTH', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _chamfer_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    # Fillet radius
    #
    _frame = gtk.Frame(_('Fillet Radius'))
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _frame.add(_fhbox)

    _label = gtk.Label(_('Radius:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _radius = "%f" % globals.prefs['FILLET_RADIUS']
    _entry.set_text(_radius)
    if not prefstate.hasWidgetKey('FILLET_RADIUS'):
        prefstate.setWidget('FILLET_RADIUS', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _fillet_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_text_opts(prefstate):
    _vbox = gtk.VBox(False, 5)

    _frame = gtk.Frame()
    _frame.set_shadow_type(gtk.SHADOW_IN)

    _text = "<span weight='bold' size='16000'>%s</span>" % _('Text Options')
    _label = gtk.Label(_text)
    _label.set_use_markup(True)
    _frame.add(_label)
    _vbox.pack_start(_frame, False, False, 5)

    _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _menu_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    
    _frame = gtk.Frame(_('Font Properties'))
    _frame.set_border_width(5)
    _fvbox = gtk.VBox(False, 5)
    _frame.add(_fvbox)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Family:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _families = prefstate.getFamilies()
    if _families is None:
        _families = []
        _window = prefstate.getWindow()        
        for _family in _window.get_pango_context().list_families():
            _families.append(_family.get_name())
        _families.sort()
        prefstate.setFamilies(_families)
    _idx = 0
    _family = globals.prefs['FONT_FAMILY']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _widget.append_text(_f)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_families)):
            _f = _families[_i]
            if _family == _f:
                _idx = _i
            _item = gtk.MenuItem(_f)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('FONT_FAMILY'):
        prefstate.setWidget('FONT_FAMILY', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Style:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _style = globals.prefs['FONT_STYLE']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_styles)):
            _name = _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_font_styles)):
            _name = _font_styles[_i]
            if _style == TextStyle.getStyleFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('FONT_STYLE'):
        prefstate.setWidget('FONT_STYLE', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Weight:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _weight = globals.prefs['FONT_WEIGHT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_font_weights)):
            _name = _font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()    
        for _i in range(len(_font_weights)):
            _name = _font_weights[_i]
            if _weight == TextStyle.getWeightFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('FONT_WEIGHT'):
        prefstate.setWidget('FONT_WEIGHT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Alignment:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _idx = 0
    _align = globals.prefs['TEXT_ALIGNMENT']
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _widget = gtk.combo_box_new_text()
        for _i in range(len(_text_align)):
            _name = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _widget.append_text(_name)
        _widget.set_active(_idx)
    else:
        _menu = gtk.Menu()
        for _i in range(len(_text_align)):
            _name = _text_align[_i]
            if _align == TextStyle.getAlignmentFromString(_name):
                _idx = _i
            _item = gtk.MenuItem(_name)
            _menu.append(_item)
        _widget = gtk.OptionMenu()
        _widget.set_menu(_menu)
        _widget.set_history(_idx)
    if not prefstate.hasWidgetKey('TEXT_ALIGNMENT'):
        prefstate.setWidget('TEXT_ALIGNMENT', _widget)
    _menu_size_group.add_widget(_widget)
    _fhbox.pack_start(_widget, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(2)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Color:'))
    _fhbox.pack_start(_label, False, False, 5)
    _color = globals.prefs['FONT_COLOR']
    _gtkcolor = gtk.gdk.color_parse(str(_color))
    if hasattr(gtk, 'ColorButton'):
        _button = gtk.ColorButton(color=_gtkcolor)
        _button.set_title(_('Select Font Color'))
        if not prefstate.hasWidgetKey('FONT_COLOR'):
            prefstate.setWidget('FONT_COLOR', _button)
    else:
        _button = gtk.Button()
        _bframe = gtk.Frame()
        _bframe.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        _bframe.set_border_width(5)
        _button.add(_bframe)
        _da = gtk.DrawingArea()
        _da.set_size_request(20, 10)
        _da.modify_bg(gtk.STATE_NORMAL, _gtkcolor)
        if not prefstate.hasWidgetKey('FONT_COLOR'):
            prefstate.setWidget('FONT_COLOR', _da)
        _button.connect("clicked", _select_font_color)
        _bframe.add(_da)
    _fhbox.pack_start(_button, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _fhbox.set_border_width(5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    _label = gtk.Label(_('Size:'))
    _label_size_group.add_widget(_label)
    _fhbox.pack_start(_label, False, False, 5)
    _entry = gtk.Entry()
    _size = "%f" % globals.prefs['TEXT_SIZE']
    _entry.set_text(_size)
    if not prefstate.hasWidgetKey('TEXT_SIZE'):
        prefstate.setWidget('TEXT_SIZE', _entry)
    _entry.connect("activate", entry_activate)
    _entry.connect("focus-out-event", _textsize_entry_focus_out, prefstate)
    _handlerid = _entry.connect("insert-text", entry_insert_text)
    _entry.set_data('handlerid', _handlerid)
    # _entry_size_group.add_widget(_entry)
    _fhbox.pack_start(_entry, False, False, 5)    
    _vbox.pack_start(_frame, False, False, 5)
    return _vbox

def _make_pref_tree(hbox, prefstate):
    _sw = gtk.ScrolledWindow()
    _sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    _sw.set_size_request(120, 300)
    _tree_store = gtk.TreeStore(gobject.TYPE_STRING,
                                gobject.TYPE_STRING)
    _iter1 = _tree_store.append(None)
    _tree_store.set(_iter1, 0, _('Basic'))
    _tree_store.set(_iter1, 1, 'basic')
    _iter1 = _tree_store.append(None)
    _tree_store.set(_iter1, 0, _('Sized Objects'))
    _tree_store.set(_iter1, 1, 'sizes')
    _iter1 = _tree_store.append(None)
    _tree_store.set(_iter1, 0, _('Text'))
    _tree_store.set(_iter1, 1, 'text')
    _tree_view = gtk.TreeView(_tree_store)
    _iter1 = _tree_store.append(None)
    _tree_store.set(_iter1, 0, _('Dimensions'))
    _tree_store.set(_iter1, 1, 'dimensions')
    _iter2 = _tree_store.append(_iter1)
    _tree_store.set(_iter2, 0, _('Primary'))
    _tree_store.set(_iter2, 1, 'primary')
    _iter2 = _tree_store.append(_iter1)
    _tree_store.set(_iter2, 0, _('Secondary'))
    _tree_store.set(_iter2, 1, 'secondary')
    _iter2 = _tree_store.append(_iter1)
    _tree_store.set(_iter2, 0, _('Linear'))
    _tree_store.set(_iter2, 1, 'linear')
    _iter2 = _tree_store.append(_iter1)
    _tree_store.set(_iter2, 0, _('Radial'))
    _tree_store.set(_iter2, 1, 'radial')
    _iter2 = _tree_store.append(_iter1)
    _tree_store.set(_iter2, 0, _('Angular'))
    _tree_store.set(_iter2, 1, 'angular')
    _tree_view.set_reorderable(False) # no drag-and-drop
    _select = _tree_view.get_selection()
    _select.set_mode(gtk.SELECTION_SINGLE)
    _select.connect("changed", tree_select_cb, prefstate)
    _renderer = gtk.CellRendererText()
    _column = gtk.TreeViewColumn(_("Options"), _renderer, text=0)
    _tree_view.append_column(_column)
    _sw.add(_tree_view)
    hbox.pack_start(_sw, False, False, 5)
    return _tree_view


def _set_dim_offset(prefstate):
    _text = prefstate.getWidget('DIM_OFFSET').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_OFFSET'] = float(_text)

def _set_dim_extension(prefstate):
    _text = prefstate.getWidget('DIM_EXTENSION').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_EXTENSION'] = float(_text)

def _set_dim_color(prefstate):
    _widget = prefstate.getWidget('DIM_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for DIM_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['DIM_COLOR'] = get_color(_r, _g, _b)

def _set_background_color(prefstate):
    _widget = prefstate.getWidget('BACKGROUND_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for BACKGROUND_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['BACKGROUND_COLOR'] = get_color(_r, _g, _b)

def _set_inactive_layer_color(prefstate):
    _widget = prefstate.getWidget('INACTIVE_LAYER_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for INACTIVE_LAYER_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['INACTIVE_LAYER_COLOR'] = get_color(_r, _g, _b)

def _set_single_point_color(prefstate):
    _widget = prefstate.getWidget('SINGLE_POINT_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for SINGLE_POINT_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['SINGLE_POINT_COLOR'] = get_color(_r, _g, _b)

def _set_multi_point_color(prefstate):
    _widget = prefstate.getWidget('MULTI_POINT_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for MULTI_POINT_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['MULTI_POINT_COLOR'] = get_color(_r, _g, _b)

def _set_font_color(prefstate):
    _widget = prefstate.getWidget('FONT_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for FONT_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['FONT_COLOR'] = get_color(_r, _g, _b)

def _set_dim_primary_font_color(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_FONT_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for DIM_PRIMARY_FONT_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['DIM_PRIMARY_FONT_COLOR'] = get_color(_r, _g, _b)

def _set_dim_secondary_font_color(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_FONT_COLOR')
    if hasattr(gtk, 'ColorButton') and isinstance(_widget, gtk.ColorButton):
        _color = _widget.get_color()
    elif isinstance(_widget, gtk.DrawingArea):
        _color= _widget.get_style().bg[gtk.STATE_NORMAL]
    else:
        raise TypeError, "Unexpected widget for DIM_SECONDARY_FONT_COLOR: " + `type(_widget)`
    _r, _g, _b = _get_rgb_values(_color)
    globals.prefs['DIM_SECONDARY_FONT_COLOR'] = get_color(_r, _g, _b)

def _set_line_thickness(prefstate):
    _text = prefstate.getWidget('LINE_THICKNESS').get_text()
    if len(_text) and _text != '+':
        globals.prefs['LINE_THICKNESS'] = float(_text)

def _set_leader_arrow_size(prefstate):
    _text = prefstate.getWidget('LEADER_ARROW_SIZE').get_text()
    if len(_text) and _text != '+':
        globals.prefs['LEADER_ARROW_SIZE'] = float(_text)

def _set_chamfer_length(prefstate):
    _text = prefstate.getWidget('CHAMFER_LENGTH').get_text()
    if len(_text) and _text != '+':
        globals.prefs['CHAMFER_LENGTH'] = float(_text)

def _set_fillet_radius(prefstate):
    _text = prefstate.getWidget('FILLET_RADIUS').get_text()
    if len(_text) and _text != '+':
        globals.prefs['FILLET_RADIUS'] = float(_text)

def _set_dim_endpoint_size(prefstate):
    _text = prefstate.getWidget('DIM_ENDPOINT_SIZE').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_ENDPOINT_SIZE'] = float(_text)

def _set_text_size(prefstate):
    _text = prefstate.getWidget('TEXT_SIZE').get_text()
    if len(_text) and _text != '+':
        globals.prefs['TEXT_SIZE'] = float(_text)

def _set_dim_primary_text_size(prefstate):
    _text = prefstate.getWidget('DIM_PRIMARY_TEXT_SIZE').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_PRIMARY_TEXT_SIZE'] = float(_text)

def _set_dim_secondary_text_size(prefstate):
    _text = prefstate.getWidget('DIM_SECONDARY_TEXT_SIZE').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_SECONDARY_TEXT_SIZE'] = float(_text)

def _set_dim_position_offset(prefstate):
    _text = prefstate.getWidget('DIM_POSITION_OFFSET').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_POSITION_OFFSET'] = float(_text)

def _set_dim_dual_mode_offset(prefstate):
    _text = prefstate.getWidget('DIM_DUAL_MODE_OFFSET').get_text()
    if len(_text) and _text != '+':
        globals.prefs['DIM_DUAL_MODE_OFFSET'] = float(_text)

def _set_dim_dual_mode(prefstate):
    _cb = prefstate.getWidget('DIM_DUAL_MODE')
    globals.prefs['DIM_DUAL_MODE'] = _cb.get_active()

def _set_highlight_points(prefstate):
    _cb = prefstate.getWidget('HIGHLIGHT_POINTS')
    globals.prefs['HIGHLIGHT_POINTS'] = _cb.get_active()

def _set_autosplit(prefstate):
    _cb = prefstate.getWidget('AUTOSPLIT')
    globals.prefs['AUTOSPLIT'] = _cb.get_active()

def _set_dim_primary_leading_zero(prefstate):
    _cb = prefstate.getWidget('DIM_PRIMARY_LEADING_ZERO')
    globals.prefs['DIM_PRIMARY_LEADING_ZERO'] =  _cb.get_active()

def _set_dim_primary_trailing_decimal(prefstate):
    _cb = prefstate.getWidget('DIM_PRIMARY_TRAILING_DECIMAL')
    globals.prefs['DIM_PRIMARY_TRAILING_DECIMAL'] = _cb.get_active()

def _set_dim_primary_precision(prefstate):
    _sb = prefstate.getWidget('DIM_PRIMARY_PRECISION')
    globals.prefs['DIM_PRIMARY_PRECISION'] = _sb.get_value_as_int()

def _set_dim_secondary_leading_zero(prefstate):
    _cb = prefstate.getWidget('DIM_SECONDARY_LEADING_ZERO')
    globals.prefs['DIM_SECONDARY_LEADING_ZERO'] = _cb.get_active()

def _set_dim_secondary_trailing_decimal(prefstate):
    _cb = prefstate.getWidget('DIM_SECONDARY_TRAILING_DECIMAL')
    globals.prefs['DIM_SECONDARY_TRAILING_DECIMAL'] = _cb.get_active()

def _set_dim_secondary_precision(prefstate):
    _sb = prefstate.getWidget('DIM_SECONDARY_PRECISION')
    globals.prefs['DIM_SECONDARY_PRECISION'] = _sb.get_value_as_int()

def _set_dim_primary_prefix(prefstate):
    _text = prefstate.getWidget('DIM_PRIMARY_PREFIX').get_text()
    globals.prefs['DIM_PRIMARY_PREFIX'] = unicode(_text)

def _set_dim_primary_suffix(prefstate):
    _text = prefstate.getWidget('DIM_PRIMARY_SUFFIX').get_text()
    globals.prefs['DIM_PRIMARY_SUFFIX'] =  unicode(_text)

def _set_dim_secondary_prefix(prefstate):
    _text = prefstate.getWidget('DIM_SECONDARY_PREFIX').get_text()
    globals.prefs['DIM_SECONDARY_PREFIX' ] = unicode(_text)

def _set_dim_secondary_suffix(prefstate):
    _text = prefstate.getWidget('DIM_SECONDARY_SUFFIX').get_text()
    globals.prefs['DIM_SECONDARY_SUFFIX'] = unicode(_text)

def _set_radial_dim_primary_prefix(prefstate):
    _text = prefstate.getWidget('RADIAL_DIM_PRIMARY_PREFIX').get_text()
    globals.prefs['RADIAL_DIM_PRIMARY_PREFIX'] = unicode(_text)

def _set_radial_dim_primary_suffix(prefstate):
    _text = prefstate.getWidget('RADIAL_DIM_PRIMARY_SUFFIX').get_text()
    globals.prefs['RADIAL_DIM_PRIMARY_SUFFIX'] = unicode(_text)

def _set_radial_dim_secondary_prefix(prefstate):
    _text = prefstate.getWidget('RADIAL_DIM_SECONDARY_PREFIX').get_text()
    globals.prefs['RADIAL_DIM_SECONDARY_PREFIX'] = unicode(_text)

def _set_radial_dim_secondary_suffix(prefstate):
    _text = prefstate.getWidget('RADIAL_DIM_SECONDARY_SUFFIX').get_text()
    globals.prefs['RADIAL_DIM_SECONDARY_SUFFIX'] = unicode(_text)

def _set_radial_dim_dia_mode(prefstate):
    _cb = prefstate.getWidget('RADIAL_DIM_DIA_MODE')
    globals.prefs['RADIAL_DIM_DIA_MODE'] = _cb.get_active()

def _set_angular_dim_primary_prefix(prefstate):
    _text = prefstate.getWidget('ANGULAR_DIM_PRIMARY_PREFIX').get_text()
    globals.prefs['ANGULAR_DIM_PRIMARY_PREFIX'] = unicode(_text)

def _set_angular_dim_primary_suffix(prefstate):
    _text = prefstate.getWidget('ANGULAR_DIM_PRIMARY_SUFFIX').get_text()
    globals.prefs['ANGULAR_DIM_PRIMARY_SUFFIX'] = unicode(_text)

def _set_angular_dim_secondary_prefix(prefstate):
    _text = prefstate.getWidget('ANGULAR_DIM_SECONDARY_PREFIX').get_text()
    globals.prefs['ANGULAR_DIM_SECONDARY_PREFIX'] = unicode(_text)

def _set_angular_dim_secondary_suffix(prefstate):
    _text = prefstate.getWidget('ANGULAR_DIM_SECONDARY_SUFFIX').get_text()
    globals.prefs['ANGULAR_DIM_SECONDARY_SUFFIX'] = unicode(_text)

def _set_drawing_units(prefstate):
    _widget = prefstate.getWidget('DRAWING_UNITS')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _unit = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _unit = _widget.get_history()
    else:
        raise TypeError, "Unexpected DRAWING_UNITS widget: " + `type(_widget)`
    globals.prefs['UNITS'] = _unit

def _set_dim_primary_units(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_UNITS')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _unit = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _unit = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_PRIMARY_UNITS widget: " + `type(_widget)`
    globals.prefs['DIM_PRIMARY_UNITS'] = _unit

def _set_dim_secondary_units(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_UNITS')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _unit = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _unit = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_SECONDARY_UNITS widget: " + `type(_widget)`
    globals.prefs['DIM_SECONDARY_UNITS'] = _unit

def _set_dim_endpoint(prefstate):
    _widget = prefstate.getWidget('DIM_ENDPOINT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_ENDPOINT widget: " + `type(_widget)`
    _endpoint = Dimension.getEndpointTypeFromString(_dim_endpoints[_idx])
    globals.prefs['DIM_ENDPOINT'] = _endpoint

def _set_dim_position(prefstate):
    _widget = prefstate.getWidget('DIM_POSITION')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_POSITION widget: " + `type(_widget)`
    _pos = Dimension.getPositionFromString(_dim_positions[_idx])
    globals.prefs['DIM_POSITION'] = _pos

def _set_font_family(prefstate):
    _widget = prefstate.getWidget('FONT_FAMILY')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected FONT_FAMILY widget: " + `type(_widget)`
    _families = prefstate.getFamilies()
    globals.prefs['FONT_FAMILY'] = _families[_idx]

def _set_font_style(prefstate):
    _widget = prefstate.getWidget('FONT_STYLE')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected FONT_STYLE widget: " + `type(_widget)`
    _style = TextStyle.getStyleFromString(_font_styles[_idx])
    globals.prefs['FONT_STYLE']= _style

def _set_font_weight(prefstate):
    _widget = prefstate.getWidget('FONT_WEIGHT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected FONT_WEIGHT widget: " + `type(_widget)`
    _weight = TextStyle.getWeightFromString(_font_weights[_idx])
    globals.prefs['FONT_WEIGHT'] = _weight

def _set_text_alignment(prefstate):
    _widget = prefstate.getWidget('TEXT_ALIGNMENT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected TEXT_ALIGNMENT widget: " + `type(_widget)`
    _align = TextStyle.getAlignmentFromString(_text_align[_idx])
    globals.prefs['TEXT_ALIGNMENT'] = _align

def _set_dim_primary_font_family(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_FONT_FAMILY')
    _families = prefstate.getFamilies()
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_PRIMARY_FONT_FAMILY widget: " + `type(_widget)`
    globals.prefs['DIM_PRIMARY_FONT_FAMILY'] = _families[_idx]

def _set_dim_primary_font_style(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_FONT_STYLE')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_PRIMARY_FONT_STYLE widget: " + `type(_widget)`
    _style = TextStyle.getStyleFromString(_font_styles[_idx])
    globals.prefs['DIM_PRIMARY_FONT_STYLE'] = _style

def _set_dim_primary_font_weight(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_FONT_WEIGHT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_PRIMARY_FONT_WEIGHT widget: " + `type(_widget)`
    _weight = TextStyle.getWeightFromString(_font_weights[_idx])
    globals.prefs['DIM_PRIMARY_FONT_WEIGHT'] = _weight

def _set_dim_primary_text_alignment(prefstate):
    _widget = prefstate.getWidget('DIM_PRIMARY_TEXT_ALIGNMENT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_PRIMARY_TEXT_ALIGNMENT widget: " + `type(_widget)`
    _align = TextStyle.getAlignmentFromString(_text_align[_idx])
    globals.prefs['DIM_PRIMARY_TEXT_ALIGNMENT'] = _align

def _set_dim_primary_font(prefstate):
    _fontsel = prefstate.getWidget('DIM_PRIMARY_FONT')
    _font = _fontsel.get_font_name()
    _family, _style, _weight, _stretch, _size = (None, None, None, None, None)
    globals.prefs['DIM_PRIMARY_FONT_FAMILY'] = _family
    globals.prefs['DIM_PRIMARY_TEXT_SIZE'] = float(_size) # fixme
    globals.prefs['DIM_PRIMARY_FONT_STYLE'] = _style
    globals.prefs['DIM_PRIMARY_FONT_WEIGHT'] = _weight

def _set_dim_secondary_font_family(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_FONT_FAMILY')
    _families = prefstate.getFamilies()
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_SECONDARY_FONT_FAMILY widget: " + `type(_widget)`
    globals.prefs['DIM_SECONDARY_FONT_FAMILY'] = _families[_idx]

def _set_dim_secondary_font_style(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_FONT_STYLE')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_SECONDARY_FONT_STYLE widget: " + `type(_widget)`
    _style = TextStyle.getStyleFromString(_font_styles[_idx])
    globals.prefs['DIM_SECONDARY_FONT_STYLE'] = _style

def _set_dim_secondary_font_weight(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_FONT_WEIGHT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_SECONDARY_FONT_WEIGHT widget: " + `type(_widget)`
    _weight = TextStyle.getWeightFromString(_font_weights[_idx])
    globals.prefs['DIM_SECONDARY_FONT_WEIGHT'] = _weight

def _set_dim_secondary_text_alignment(prefstate):
    _widget = prefstate.getWidget('DIM_SECONDARY_TEXT_ALIGNMENT')
    if hasattr(gtk, 'ComboBox') and isinstance(_widget, gtk.ComboBox):
        _idx = _widget.get_active()
    elif isinstance(_widget, gtk.OptionMenu):
        _idx = _widget.get_history()
    else:
        raise TypeError, "Unexpected DIM_SECONDARY_TEXT_ALIGNMENT widget: " + `type(_widget)`
    _align = TextStyle.getAlignmentFromString(_text_align[_idx])
    globals.prefs['DIM_SECONDARY_TEXT_ALIGNMENT'] = _align

def _set_dim_secondary_font(prefstate):
    _fontsel = prefstate.getWidget('DIM_SECONDARY_FONT')
    _font = _fontsel.get_font_name()
    _family, _style, _weight, _stretch, _size = (None, None, None, None, None)
    globals.prefs['DIM_SECONDARY_FONT_FAMILY'] = _family
    globals.prefs['DIM_SECONDARY_TEXT_SIZE'] = float(_size) # fixme
    globals.prefs['DIM_SECONDARY_FONT_STYLE'] = _style
    globals.prefs['DIM_SECONDARY_FONT_WEIGHT'] = _weight
    
_keymap = {
    'DIM_OFFSET' : _set_dim_offset,
    'DIM_EXTENSION' : _set_dim_extension,
    'DIM_COLOR' : _set_dim_color,
    'BACKGROUND_COLOR' : _set_background_color,
    'INACTIVE_LAYER_COLOR' : _set_inactive_layer_color,
    'SINGLE_POINT_COLOR' : _set_single_point_color,
    'MULTI_POINT_COLOR' : _set_multi_point_color,
    'FONT_COLOR' : _set_font_color,
    'DIM_PRIMARY_FONT_COLOR' : _set_dim_primary_font_color,
    'DIM_SECONDARY_FONT_COLOR' : _set_dim_secondary_font_color,
    'LINE_THICKNESS' : _set_line_thickness,
    'LEADER_ARROW_SIZE' : _set_leader_arrow_size,
    'CHAMFER_LENGTH' : _set_chamfer_length,
    'FILLET_RADIUS' : _set_fillet_radius,
    'HIGHLIGHT_POINTS' : _set_highlight_points,
    'AUTOSPLIT' : _set_autosplit,
    'DIM_PRIMARY_FONT_FAMILY' : _set_dim_primary_font_family,
    'DIM_PRIMARY_FONT_STYLE' : _set_dim_primary_font_style,
    'DIM_PRIMARY_FONT_WEIGHT' : _set_dim_primary_font_weight,
    'DIM_PRIMARY_TEXT_SIZE' : _set_dim_primary_text_size,
    'DIM_PRIMARY_TEXT_ALIGNMENT' : _set_dim_primary_text_alignment,
    'DIM_PRIMARY_PRECISION' : _set_dim_primary_precision,
    'DIM_PRIMARY_LEADING_ZERO' : _set_dim_primary_leading_zero,
    'DIM_PRIMARY_TRAILING_DECIMAL' : _set_dim_primary_trailing_decimal,
    'DIM_SECONDARY_FONT_FAMILY' : _set_dim_secondary_font_family,
    'DIM_SECONDARY_FONT_STYLE' : _set_dim_secondary_font_style,
    'DIM_SECONDARY_FONT_WEIGHT' : _set_dim_secondary_font_weight,
    'DIM_SECONDARY_TEXT_SIZE' : _set_dim_secondary_text_size,
    'DIM_SECONDARY_TEXT_ALIGNMENT' : _set_dim_secondary_text_alignment,
    'DIM_SECONDARY_PRECISION' : _set_dim_secondary_precision,
    'DIM_SECONDARY_LEADING_ZERO' : _set_dim_secondary_leading_zero,
    'DIM_SECONDARY_TRAILING_DECIMAL' : _set_dim_secondary_trailing_decimal,
    'DIM_PRIMARY_PREFIX' : _set_dim_primary_prefix,
    'DIM_PRIMARY_SUFFIX' : _set_dim_primary_suffix,
    'DIM_SECONDARY_PREFIX' : _set_dim_secondary_prefix,
    'DIM_SECONDARY_SUFFIX' : _set_dim_secondary_suffix,
    'RADIAL_DIM_PRIMARY_PREFIX' : _set_radial_dim_primary_prefix,
    'RADIAL_DIM_PRIMARY_SUFFIX' : _set_radial_dim_primary_suffix,
    'RADIAL_DIM_SECONDARY_PREFIX' : _set_radial_dim_secondary_prefix,
    'RADIAL_DIM_SECONDARY_SUFFIX' : _set_radial_dim_secondary_suffix,
    'RADIAL_DIM_DIA_MODE' : _set_radial_dim_dia_mode,
    'ANGULAR_DIM_PRIMARY_PREFIX' : _set_angular_dim_primary_prefix,
    'ANGULAR_DIM_PRIMARY_SUFFIX' : _set_angular_dim_primary_suffix,
    'ANGULAR_DIM_SECONDARY_PREFIX' : _set_angular_dim_secondary_prefix,
    'ANGULAR_DIM_SECONDARY_SUFFIX' : _set_angular_dim_secondary_suffix,
    'DRAWING_UNITS' : _set_drawing_units,
    'DIM_PRIMARY_UNITS' : _set_dim_primary_units,
    'DIM_SECONDARY_UNITS' : _set_dim_secondary_units,
    'FONT_FAMILY' : _set_font_family,
    'FONT_STYLE' : _set_font_style,
    'FONT_WEIGHT' : _set_font_weight,
    'TEXT_SIZE' : _set_text_size,
    'TEXT_ALIGNMENT' : _set_text_alignment,
    'DIM_PRIMARY_FONT' : _set_dim_primary_font,
    'DIM_SECONDARY_FONT' : _set_dim_secondary_font,
    'DIM_ENDPOINT' : _set_dim_endpoint,
    'DIM_ENDPOINT_SIZE' : _set_dim_endpoint_size,
    'DIM_DUAL_MODE' : _set_dim_dual_mode,
    'DIM_POSITION' : _set_dim_position,
    'DIM_DUAL_MODE_OFFSET' : _set_dim_dual_mode_offset,
    'DIM_POSITION_OFFSET' : _set_dim_position_offset,
    }

def apply_prefs(prefstate):
    for _key in prefstate.getWidgetKeys():
        # print "widget key: " + _key
        if _key in _keymap:
            _optfunc = _keymap[_key]
            _optfunc(prefstate)
        # else:
            # print "no function for " + _key

def prefs_dialog(gtkimage):
    _window = gtkimage.getWindow()
    _prefstate = Prefstate()
    _prefstate.setImage(gtkimage.image)
    _prefstate.setWindow(_window)
    _dialog = gtk.Dialog(_('Set Preferences'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 5)
    _prefstate.setHBox(_hbox)
    _hbox.set_border_width(5)
    _dialog.vbox.pack_start(_hbox, True, True)
    _tree_view = _make_pref_tree(_hbox, _prefstate)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        apply_prefs(_prefstate)
        preferences.save_user_prefs()
    _prefstate.clear()
    _dialog.destroy()
