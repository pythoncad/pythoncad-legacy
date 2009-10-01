#
# Copyright (c) 2004, 2006, 2007 Art Haas
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
# code for setting printing parameters
#

import pygtk
pygtk.require('2.0')
import gtk

import os
import tempfile

from PythonCAD.Generic.plotfile import Plot
from PythonCAD.Generic.printing import PSPlot

def _toggle_widgets_on(widget):
    widget.set_sensitive(True)

def _toggle_widgets_off(widget):
    widget.set_sensitive(False)

def _print_rb_cb(button, hbox):
    if button.get_active():
        hbox.foreach(_toggle_widgets_on)
    else:
        hbox.foreach(_toggle_widgets_off)
    return True

def _error_dialog(gtkimage, errmsg):
    _window = gtkimage.getWindow()
    _dialog = gtk.MessageDialog(_window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 gtk.MESSAGE_ERROR,
                                 gtk.BUTTONS_CLOSE,
                                 errmsg)
    _dialog.run()
    _dialog.destroy()

def print_dialog(gtkimage, plot):
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Printing Preferences'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _vbox = _dialog.vbox
    #
    _psplot = PSPlot(plot)
    #
    # options for all plots
    #
    _frame = gtk.Frame(_('Plot Options'))
    _fvbox = gtk.VBox(False, 5)
    _fvbox.set_border_width(5)
    _frame.add(_fvbox)
    _ccb = gtk.CheckButton(_('Print in Color'))
    _fvbox.pack_start(_ccb, False, False, 5)
    _icb = gtk.CheckButton(_('Print White as Black'))
    _fvbox.pack_start(_icb, False, False, 5)
    _lcb = gtk.CheckButton(_('Print in Landscape Mode'))
    _fvbox.pack_start(_lcb, False, False, 5)
    _hbox = gtk.HBox(False, 5)
    _fvbox.pack_start(_hbox, True, True, 5)
    _label = gtk.Label(_('Paper Size:'))
    _hbox.pack_start(_label, False, False, 5)
    _papersizes = _psplot.getPaperSizes()
    _papersizes.sort()
    if hasattr(gtk, 'ComboBox'): # PyGTK 2.4
        _size_widget = gtk.combo_box_new_text()
        for _size in _papersizes:
            _size_widget.append_text(_size)
        _size_widget.set_active(0) # perhaps a global preferences value?
    else:
        _menu = gtk.Menu()
        for _size in _papersizes:
            _item = gtk.MenuItem(_size)
            _menu.append(_item)
        _size_widget = gtk.OptionMenu()
        _size_widget.set_menu(_menu)
        _size_widget.set_history(0) # perhaps a global preference value?
    _hbox.pack_start(_size_widget, False, False, 5)
    _vbox.pack_start(_frame, False, False, 5)
    #
    #
    _label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    _frame = gtk.Frame(_('Print Destination'))
    _fvbox = gtk.VBox(False, 5)
    _fvbox.set_border_width(5)
    _frame.add(_fvbox)
    #
    _phbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('Printer:'))
    _label_size_group.add_widget(_label)
    _phbox.pack_start(_label, False, False, 5)
    _print_entry = gtk.Entry()
    _print_entry.set_text("lp")
    _phbox.pack_start(_print_entry, False, False, 5)
    _fvbox.pack_start(_phbox, False, False, 5)
    #
    _fhbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('File:'))
    _label_size_group.add_widget(_label)
    _label.set_sensitive(False)
    _fhbox.pack_start(_label, False, False, 5)
    _file_entry = gtk.Entry()
    _file_entry.set_sensitive(False)
    _fhbox.pack_start(_file_entry, False, False, 5)
    _fvbox.pack_start(_fhbox, False, False, 5)
    #
    _hbox = gtk.HBox(False, 5)
    _label = gtk.Label(_('Send print to ...'))
    _label_size_group.add_widget(_label)
    _hbox.pack_start(_label, False, False, 5)
    _prb = gtk.RadioButton()
    _prb.set_label(_('Printer'))
    _prb.set_mode(True)
    _prb.connect("toggled", _print_rb_cb, _phbox)
    _hbox.pack_start(_prb, False, False, 5)
    _frb = gtk.RadioButton(_prb)
    _frb.set_label(_('File'))
    _frb.set_mode(True)
    _frb.connect("toggled", _print_rb_cb, _fhbox)
    _hbox.pack_start(_frb, False, False, 5)
    _fvbox.pack_start(_hbox, False, False, 5)
    #
    _vbox.pack_start(_frame, False, False, 5)
    _dialog.show_all()
    while True:
        _response = _dialog.run()
        if _response == gtk.RESPONSE_OK:
            plot.setColorMode(_ccb.get_active())
            plot.invertWhite(_icb.get_active())
            plot.setLandscapeMode(_lcb.get_active())
            plot.getPlotData()
            if hasattr(gtk, 'ComboBox') and isinstance(_size_widget, gtk.ComboBox):
                _idx = _size_widget.get_active()
            elif isinstance(_size_widget, gtk.OptionMenu):
                _idx = _sizewidget.get_history()
            else:
                raise TypeError, "Unexpected size_widget: " + `type(_size_widget)`
            _psplot.setSize(_papersizes[_idx])
            if _prb.get_active(): # send job out
                try:
                    _f = tempfile.NamedTemporaryFile()
                    _fname = _f.name
                    try:
                        try:
                            _psplot.write(_f)
                            _cmd = "%s %s" %(_print_entry.get_text(), _fname)
                            try:
                                _res = os.system(_cmd)
                                if _res == 0:
                                    break
                                else:
                                    _msg = "Non-zero exit status from '%s': %d" % (_cmd, _res)
                                    _error_dialog(gtkimage, _msg)
                            except StandardError, _err:
                                _msg = "Error executing command '%s': %s" % (_cmd, _err)
                                _error_dialog(gtkimage, _msg)
                        except StandardError, _err:
                            _msg = "Error writing '%s': %s" % (_fname, _err)
                            _error_dialog(gtkimage, _msg)
                    finally:
                        _f.close()
                except StandardError, _err:
                    _msg = "Error creating temporary file %s" % _err
                    _error_dialog(gtkimage, _msg)
            else:
                _fname = _file_entry.get_text()
                try:
                    _f = file(_fname, "w")
                    try:
                        _psplot.write(_f)
                    finally:
                        _f.close()
                        break
                except StandardError, _err:
                    _msg = "Error writing to %s: %s" % (_fname, _err)
                    _error_dialog(gtkimage, _msg)
        else:
            break
    _psplot.finish()        
    _dialog.destroy()

def _show_print_dialog(gtkimage, tool=None):
    _plot = Plot(gtkimage.image)
    _tool = gtkimage.getImage().getTool()
    _x1, _y1 = _tool.getFirstCorner()
    _x2, _y2 = _tool.getSecondCorner()
    _xmin = min(_x1, _x2)
    _ymin = min(_y1, _y2)
    _xmax = max(_x1, _x2)
    _ymax = max(_y1, _y2)
    _plot.setBounds(_xmin, _ymin, _xmax, _ymax)
    _tool.reset()
    plot_mode_init(gtkimage)
    gtkimage.refresh()
    print_dialog(gtkimage, _plot)

def plot_motion_notify(gtkimage, widget, event, tool):
    _tx, _ty = tool.getFirstCorner()
    _px, _py = gtkimage.coordToPixTransform(_tx, _ty)
    _gc = gtkimage.getGC()
    _x = int(event.x)
    _y = int(event.y)
    _cp = tool.getCurrentPoint()
    if _cp is not None:
        _xc, _yc = _cp
        _xmin = min(_xc, _px)
        _ymin = min(_yc, _py)
        _rw = abs(_xc - _px)
        _rh = abs(_yc - _py)
        widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    tool.setCurrentPoint(_x, _y)
    _xmin = min(_x, _px)
    _ymin = min(_y, _py)
    _rw = abs(_x - _px)
    _rh = abs(_y - _py)
    widget.window.draw_rectangle(_gc, False, _xmin, _ymin, _rw, _rh)
    return True

def _make_tuple(text, gdict):
    _tpl = eval(text, gdict)
    if not isinstance(_tpl, tuple):
        raise TypeError, "Invalid tuple: " + `type(_tpl)`
    if len(_tpl) != 2:
        raise ValueError, "Invalid tuple: " + str(_tpl)
    return _tpl

def plot_second_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _x, _y = _image.getClosestPoint(_x, _y, tolerance=_tol)
    tool.setSecondCorner(_x, _y)
    _show_print_dialog(gtkimage, tool)
    return True

def plot_second_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = _make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setSecondCorner(_x, _y)
        _show_print_dialog(gtkimage, tool)

def plot_first_button_press_cb(gtkimage, widget, event, tool):
    _tol = gtkimage.getTolerance()
    _image = gtkimage.getImage()
    _x, _y = _image.getCurrentPoint()
    _x, _y = _image.getClosestPoint(_x, _y, tolerance=_tol)
    tool.setFirstCorner(_x, _y)
    gtkimage.setPrompt(_('Click in the drawing area or enter another point'))
    tool.setHandler("button_press", plot_second_button_press_cb)
    tool.setHandler("entry_event", plot_second_entry_event_cb)
    tool.setHandler("motion_notify", plot_motion_notify)
    gtkimage.getGC().set_function(gtk.gdk.INVERT)
    return True
        
def plot_first_entry_event_cb(gtkimage, widget, tool):
    _entry = gtkimage.getEntry()
    _text = _entry.get_text()
    _entry.delete_text(0,-1)
    if len(_text):
        _x, _y = _make_tuple(_text, gtkimage.image.getImageVariables())
        tool.setFirstCorner(_x, _y)
        gtkimage.setPrompt(_('Click in the drawing area or enter another point'))
        tool.setHandler("button_press", plot_second_button_press_cb)
        tool.setHandler("entry_event", plot_second_entry_event_cb)
        tool.setHandler("motion_notify", plot_motion_notify)
        gtkimage.getGC().set_function(gtk.gdk.INVERT)

def plot_mode_init(gtkimage, tool=None):
    gtkimage.setPrompt(_('Click in the drawing area or enter a point'))
    _tool = gtkimage.getImage().getTool()
    _tool.setHandler("initialize", plot_mode_init)
    _tool.setHandler("button_press", plot_first_button_press_cb)
    _tool.setHandler("entry_event", plot_first_entry_event_cb)
