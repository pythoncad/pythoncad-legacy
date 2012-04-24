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
# Qt Import
#

from PyQt4.QtGui    import QDialog,QAbstractItemView
from PyQt4.QtCore   import pyqtSignature

from Ui_property    import Ui_Dialog

from Interface.cadinitsetting import *
from Interface.Dialogs.dataModel import populateTable

class Property(QDialog, Ui_Dialog):
    """
        this class define the entity property dialog
        it automaticaly retrive the style property 
        and show it in the form
    """
    def __init__(self, parent = None, entity=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.containers={}
        self._isOk=False
        self.entity=entity
        styleprops=entity[0].style.props
        for propName in styleprops:
            val=styleprops[propName]
            if propName in PYTHONCAD_STYLE_WIDGET:
                propDescription=PYTHONCAD_STYLE_DESCRIPTION[propName]
                self.containers[propName]=PYTHONCAD_STYLE_WIDGET[propName](None, oldValue=val,label=propDescription)
                self.propertyConteiner.addLayout(self.containers[propName])
        self.populateCustomProperty()
        self.exec_()
    
    def populateCustomProperty(self):
        """
            populate the dialog with the custom property
        """
        #tableObject=self.entity[0]._entity.properties
        tableObject=[['name','10'],['dimension','20']]
        populateTable(self.customProperty,tableObject,['Name','Value'])
     
        
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
            implements the accept button
        """
        self._isOk=True
        self.close()
        
    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
            implements the accept button
        """
        self._isOk=False
        self.close()
    @property 
    def changed(self):
        """
            tells if the object is changed
        """
        return self._isOk
        
    @property
    def value(self):
        exitVal={}
        if self.changed:
            for name in self.containers:
                obj=self.containers[name]
                if obj.changed:
                    exitVal[name]=obj.value
        return exitVal
