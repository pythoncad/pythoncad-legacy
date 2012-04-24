
##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 23/apr/2012 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    info@omniasolutions.eu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''    
Created on 23/apr/2012
@author: mboscolo
'''

from  PyQt4.QtCore    import *
from  PyQt4.QtGui     import *

class DataModel(QAbstractTableModel): 
    """
        abstract model for manage values
    """
    def __init__(self, datain, headerdata, parent=None, *args): 
        QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata 
        flags=[]      
        flags.append(Qt.ItemIsEditable)
        flags.append(Qt.ItemIsSelectable)
        flags.append(Qt.ItemIsEnabled)
        self._flags=flags
        
    def rowCount(self,objParent): 
        """
            row count
        """
        return len(self.arraydata) 
    
    def addNewRow(self):
        """
            add a new empty row to the abstract model
        """
        newRow=[]
        newRow.append(False)
        for i in range(1,len(self.headerdata)):
            newRow.append('')
        self.insertRow(self.rowCount(None)+1,[newRow]) 

    def insertRow(self, pos, row):
        """
            insert row
        """
        self.insertRows(pos, 1, row)
        self.emit(SIGNAL('layoutChanged()'))
  
    def insertRows(self, pos, count, rows):
        """
            insert rows
        """
        self.beginInsertRows(QModelIndex(), pos, pos + count - 1)
        for row in rows:
            self.arraydata.append(row)
        self.endInsertRows()
        self.emit(SIGNAL('layoutChanged()'))
        return True
    
    def removeRow(self, pos):
        """
            remove row
        """
        self.removeRows(pos, 1)
        return True
  
  
    def removeRows(self, row=-1, count=0, parent=QModelIndex()):
        """
            remove rows
        """
        if row == -1:
            self.beginRemoveRows(QModelIndex(), 0, len(self.arraydata) - 1)
            del self.arraydata[:]
        else:
            self.beginRemoveRows(QModelIndex(), row, row + count - 1)
            del self.arraydata[row:row + count]
        self.endRemoveRows()
        self.emit(SIGNAL('layoutChanged()'))
        return True
    
    def columnCount(self, parent): 
        """
            return the column count
        """
        if len(self.arraydata)>0:
            return len(self.arraydata[0])
        return 0 
    
    def _rule(self,index):
        """
            this class must be overloaded in order to control the background color
        """
        return False
    
    def backgroudIndex(self,index):
        if self._rule(index):
            self.setData(index, Qt.QColor(Qt.red), Qt.BackgroundColorRole)
    
    def data(self, index, role): 
        if not index.isValid(): 
            return QVariant() 
        elif role != Qt.DisplayRole: 
            return QVariant() 
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()

    def flags(self, index):
        """
            set the flag for the data model
        """
        flags = super(self.__class__,self).flags(index)
        for flag in self._flags:
            flags |= flag
            
        #flags |= QtCore.Qt.ItemIsDragEnabled
        #flags |= QtCore.Qt.ItemIsDropEnabled
        return flags
    
    def enableRowEdit(self,index):
        """
            
        """
        pass
    
    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        col = index.column()
        self.arraydata[row][col] = str(value.toString())
        self.emit(SIGNAL('dataChanged()'))
        return True
    
    def getRowData(self,index):
        return self.arraydata[index.row()]

def populateTable(refTable,tableObject,header,backGroundFunction=False):
    """
        Create the table elements
    """
    modelTable=DataModel(tableObject,header)
    modelTable._flags=[Qt.ItemIsSelectable,Qt.ItemIsEnabled,Qt.ItemIsEditable]
    if backGroundFunction!=False:
        modelTable._rule=backGroundFunction
    refTable.setModel(modelTable)
    #
    # Set Table Behavior
    #
    refTable.resizeColumnsToContents()
    vh = refTable.verticalHeader()
    vh.setVisible(False)
    refTable.setAlternatingRowColors(True)
    # set horizontal header properties
    hh = refTable.horizontalHeader()
    hh.setStretchLastSection(True)
    # set column width to fit contents
    refTable.resizeColumnsToContents()
    # set row height
    nrows = len(tableObject)
    for row in xrange(nrows):
        refTable.setRowHeight(row, 18)
    #
    # Set Selection
    #        
    refTable.setEditTriggers(QAbstractItemView.DoubleClicked)
    refTable.setSelectionBehavior(QAbstractItemView.SelectRows)
    refTable.setSelectionMode(QAbstractItemView.ExtendedSelection) 