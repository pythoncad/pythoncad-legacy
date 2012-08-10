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

from PyQt4.QtGui    import QDialog,QAbstractItemView,QMenu,QAction
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
        self.customProperty.contextMenuEvent=self.customPropertyContextMenuEvent
        for propName in styleprops:
            val=styleprops[propName]
            if propName in PYTHONCAD_STYLE_WIDGET:
                propDescription=PYTHONCAD_STYLE_DESCRIPTION[propName]
                self.containers[propName]=PYTHONCAD_STYLE_WIDGET[propName](None, oldValue=val,label=propDescription)
                self.propertyConteiner.addLayout(self.containers[propName])
        self.populateCustomProperty(styleprops)
        self.exec_()
    
    def populateCustomProperty(self,styleprops):
        """
            populate the dialog with the custom property
        """
        tableObject=[[k,v] for k,v in styleprops.get('property',{}).items()]
        populateTable(self.customProperty,tableObject,['Name','Value'])
     
     
    def customPropertyContextMenuEvent(self,event):
        contexMenu=QMenu(self)
        #
        # Create Actions
        #
        newAction   =   QAction("New", self, triggered=self._newCustomProperty)
        delAction   =   QAction("Delete", self, triggered=self._delCustomProperty)  
        #
        # Add action to the context menu   
        #
        contexMenu.addAction(newAction)
        contexMenu.addAction(delAction)
        #
        contexMenu.exec_(event.globalPos())
        del(contexMenu)       
    
    def _newCustomProperty(self):
        """
            Open an empty ParameterUi
        """
        self.customProperty.model().addNewRow()
                
    def _delCustomProperty(self):
        """
            Edit the selected parameter values
        """
        rows=self.customProperty.selectionModel().selectedRows()
        if len(rows)>0:
            row=rows[0]
            self.customProperty.model().removeRow(row.row())
    
    def uppdateCustomProperty(self):
        """
            update the custom property
        """ 
        self._properties = dict(self.customProperty.model().arraydata)

    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
            implements the accept button
        """
        self.uppdateCustomProperty()
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
        #Update custom propertis
        if len(self._properties)>0:
            exitVal['property']=self._properties
        return exitVal
