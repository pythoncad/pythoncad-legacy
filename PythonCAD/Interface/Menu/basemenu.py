#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo, Gertwin Groen
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the termscl_bo of the GNU General Public License as published by
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

import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms


from PythonCAD.Interface.Gtk import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
from PythonCAD.Interface.Gtk import gtkprinting
from PythonCAD.Interface.Gtk import gtkactions
from PythonCAD.Generic import globals
from PythonCAD.Generic import fileio
from PythonCAD.Generic import imageio
from PythonCAD.Generic import tools
from PythonCAD.Generic import plotfile
from PythonCAD.Generic import text
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import dimension
from PythonCAD.Generic import extFormat

from PythonCAD.Generic.image import Image
from PythonCAD.Interface.Gtk import gtkdimprefs
from PythonCAD.Interface.Gtk import gtktextprefs
from PythonCAD.Interface.Gtk import gtkstyleprefs
from PythonCAD.Interface.Gtk import gtkdialog as gtkDialog



def error_dialog(gtkimage, errmsg):
    _window = gtkimage.getWindow()
    _dialog = gtk.MessageDialog( _window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 gtk.MESSAGE_ERROR,
                                 gtk.BUTTONS_CLOSE,
                                 errmsg)
    _dialog.run()
    _dialog.destroy()


#############################################################################
#
# class IBaseMenu
#
#############################################################################

class IBaseMenu(object):

    # --------------------------------------------------------------------------------------------
    def __init__(self, parent):
        self.gtkimage = parent

    # --------------------------------------------------------------------------------------------
    def _add_accelerators(self, action, menuitem, accelgroup):
        _path = action.get_accel_path()
        if _path is not None:
            _data = gtk.accel_map_lookup_entry(_path)
            if _data is not None:
                _k, _m = _data
                if gtk.accelerator_valid(_k, _m):
                    menuitem.add_accelerator('activate', accelgroup, _k, _m, gtk.ACCEL_VISIBLE)

