#
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
#
# Functions For handling PythonCad Dialogs
#
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import os

ioDebug=True

def _error_dialog(gtkimage, errmsg):
    """
        Show an error dialog
    """
    _window = gtkimage.getWindow()

    _dialog =  gtk.Dialog(_('PythonCad Error'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _label = gtk.Label(errmsg)
    _dialog.vbox.pack_start(_label, True, True, 0)
    _label.show()
    _dialog.show_all()
    _response = _dialog.run()
    _dialog.destroy()
    if ioDebug :
        for s in sys.exc_info():
            print "Exception Error: %s"%str(s)

def _message_dialog(gtkimage,label1,label2):
    """
        Create a dialogo with two label to give more information at the user
    """
    _window = gtkimage.getWindow()
    _dialog =  gtk.Dialog(_('PythonCad Message'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _label1 = gtk.Label(label1)
    _label2 = gtk.Label(label2)
    _dialog.vbox.pack_start(_label1, True, True, 0)
    _dialog.vbox.pack_start(_label2, True, True, 0)
    _label1.show()
    _label2.show()
    _dialog.show_all()
    _response = _dialog.run()
    _dialog.destroy()
    
def _yesno_dialog(gtkimage,label):
    """
        Create a dialogo with a label and a yes no button
    """
    _window = gtkimage.getWindow()
    _dialog =  gtk.Dialog(_('PythonCad Message'), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
                         
    _label = gtk.Label(label)
    _dialog.vbox.pack_start(_label, True, True, 0)
    _label.show()
    _dialog.show_all()
    _response = _dialog.run()
    _dialog.destroy()   
    return _response

def delete_event(widget, event, data=None):
        gtk.main_quit()
        return False
   
    
def _help_dialog(gtkimage,Command):
    """
        Show the help dialog for the specifie comand
        Need to be implemented
        1) open a child windows that show html text
        2) load the command file 
    """
    pass

def abautDialog():
    """
        Show The application debug dialog
    """
    _abautDialog=gtk.AboutDialog()
    _abautDialog.set_name("PythonCad")
    _abautDialog.set_program_name("PythonCad")
    _abautDialog.set_version("DS1-R38-Alfa")
    _abautDialog.set_comments("CAD built from Python")
    _iconPath=os.path.join(os.getcwd(),"gtkpycad.png")
    _pixBuf=gtk.gdk.pixbuf_new_from_file(_iconPath)
    _abautDialog.set_logo(_pixBuf)
    _abautDialog.set_website("http://sourceforge.net/projects/pythoncad")
    _licMsg='PythonCAD is distributed in the hope that it will be useful, \n \
        but WITHOUT ANY WARRANTY; without even the implied warranty of \n \
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \n \
        GNU General Public License for more details. \n \
        You should have received a copy of the GNU General Public License \n \
        along with PythonCAD; if not, write to the Free Software \n \
        Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA'
    _abautDialog.set_license(_licMsg)
    response = _abautDialog.run()
    _abautDialog.destroy()

def reportDialog(gtkimage,title,strArray):
    """
        Create a report dialog 
    """
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_(title), _window,
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _tb = gtk.TextBuffer()
    _tv = gtk.TextView(_tb)
    _tv.set_editable(False)
    _sw = gtk.ScrolledWindow()
    _sw.set_size_request(400, 300)
    _sw.add_with_viewport(_tv)
    _dialog.vbox.pack_start(_sw, True, True, 0)
    _dialog.show_all()
    for _s in strArray:
        try:
            _s=util.to_unicode(_s)
        except:
            pass
        _tb.insert_at_cursor(_s)
    _response = _dialog.run()
    
    _dialog.destroy()
