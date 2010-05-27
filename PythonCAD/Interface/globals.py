#
# Copyright (c) 2010 Matteo Boscolo, Gertwin Groen
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
# This module contain global functions
#

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

#from Generic.Kernel.application import Application
#from Interface.cadwindow import CadWindow


# kernel application object
global_application = None
# main application window
global_cad_window = None


def CadWindow():
    '''
    Gets the main window.
    The main window is an instance of the CadWindow object.
    '''
    return global_cad_window


def Application():
    '''
    Gets the application object from the kernel.
    '''
    return global_application;


def critical(text):
    dlg = QtGui.QMessageBox()
    dlg.setText(text)
    dlg.setIcon(QtGui.QMessageBox.Critical)
    dlg.exec_()
    return

