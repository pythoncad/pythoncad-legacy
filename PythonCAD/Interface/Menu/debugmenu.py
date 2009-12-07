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

import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms

#from PythonCAD.Interface.Gtk.self.gtkimage import GTKImage

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

from PythonCAD.Interface.Menu.basemenu import IBaseMenu


#############################################################################
#
# callbacks for the menu items
#
#############################################################################

def get_focus_widget_cb(menuitem, gtkimage):
    _widget = gtkimage.getWindow().get_focus()
    print "Focus widget: " + str(_widget)

def get_undo_stack_cb(menuitem, gtkimage):
    _layer = gtkimage.image.getActiveLayer()
    _log = _layer.getLog()
    if _log is not None:
        _log.printUndoData()

def get_redo_stack_cb(menuitem, gtkimage):
    _layer = gtkimage.image.getActiveLayer()
    _log = _layer.getLog()
    if _log is not None:
        _log.printRedoData()

def get_image_undo_cb(menuitem, gtkimage):
    gtkimage.image.printStack(True)

def get_image_redo_cb(menuitem, gtkimage):
    gtkimage.image.printStack(False)

def collect_garbage_cb(menuitem, gtkimage):
    if 'gc' in sys.modules:
        _lost = gc.collect()
        print "%d lost objects: " % _lost


def _debug_cb(action, *args):
    print "_debug_cb()"
    print "action: " + `action`
    print "args: " + str(args)
    _group = action.get_property('action-group')
    if _group is not None:
        for _act in _group.list_actions():
            _name = _act.get_name()
            print "Action name: %s" % _name


    
#############################################################################
#
# class IDebugMenu
#
#############################################################################

class IDebugMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IDebugMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Debug')
        self.gtkimage.addGroup(group)
        action = gtk.Action('DebugMenu', _('_Debug'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "DebugMenu object.")


#----------------------------------------------------------------------------------------------
#############################################################################
#   Top level snap menu
#############################################################################
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        _act = gtk.Action('Focus', _('Focus'), None, None)
        _act.connect('activate', get_focus_widget_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('UndoStack', _('Undo Stack'), None, None)
        _act.connect('activate', get_undo_stack_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, '<alt>Z')
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('RedoStack', _('Redo Stack'), None, None)
        _act.connect('activate', get_redo_stack_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, '<alt><shift>Z')
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('ImageUndo', _('Image Undo'), None, None)
        _act.connect('activate', get_image_undo_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('ImageRedo', _('Image Redo'), None, None)
        _act.connect('activate', get_image_redo_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('GC', 'GC', None, None)
        _act.connect('activate', collect_garbage_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        return _menu
 
        

#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem):
        pass

        
               
               