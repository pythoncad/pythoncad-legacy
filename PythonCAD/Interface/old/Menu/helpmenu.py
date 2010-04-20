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
# This is the creation of the help Menu
#
import os
import stat
import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms

from PythonCAD.Interface.Menu.basemenu import IBaseMenu

#############################################################################
#
# callbacks for the menu items
#
#############################################################################

def  show_abaut_cb(menuitem, gtkimage):
    """
        CallBack action for the about menu
    """
    import PythonCAD.Interface.Gtk.gtkdialog as dialog
    dialog.abautDialog()
    

class IHelpMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IHelpMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Help')
        self.gtkimage.addGroup(group)
        action = gtk.Action('HelpMenu', _('_Help'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "HelpMenu object.")

#----------------------------------------------------------------------------------------------
#############################################################################
#   Top level snap menu
#############################################################################
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        _act = gtk.Action('About', _('About'), None, None)
        _act.connect('activate', show_abaut_cb, self.gtkimage)
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
    