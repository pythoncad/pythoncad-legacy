#
# Copyright (c) 2010,2011 Matteo Boscolo
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
# This Module provide a Interface Command managing the preview the and the snap
# system
#
# How it works:
# 
#
#
#Qt Import
#

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature

from Ui_property import Ui_Dialog

from Interface.cadinitsetting import *

class Property(QDialog, Ui_Dialog):
    """
        this class define the entity property dialog
        it automaticaly retrive the style property 
        and show it in the form
    """
    def __init__(self, parent = None, entity=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        styleprops=entity[0].style.props
        for propName in styleprops:
            val=styleprops[propName]
            if propName in PYTHONCAD_STYLE_WIDGET:
                container=PYTHONCAD_STYLE_WIDGET[propName](oldValue=val,label=propName)
                self.propertyConteiner.addLayout(container)
        
        self.exec_()
        
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
            implements the accept button
        """
        # TODO: not implemented yet
        raise NotImplementedError
        
    @property
    def value(self):
        #qui mettere a posto tutte le propieta se sono cambiate
        #se no null
        return null
