#
# Copyright (c) 2010 Matteo Boscolo
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
# This  module provide access to the undo part of the pythoncad database
#

from  pycadbasedb import PyCadBaseDb

class PyCadUndoDb(PyCadBaseDb):
    """
        this Class Provide all the basic operation to be made on the
        undo 
    """
    def __init__(self,dbConnection):
        PyCadBaseDb.__init__(self)
        if dbConnection is None:
            self.createConnection()
        else:
            self.setConnection(dbConnection)     
        _sqlCheck="""select * from sqlite_master where name like 'pycadundo'"""
        _table=self.makeSelect(_sqlCheck).fetchone()
        if _table is None:
            _sqlCreation="""CREATE TABLE "pycadundo" (
                                "pycad_id" INTEGER PRIMARY KEY,
                                "pycad_ent_id" INTEGER ,
                                "pycad_undo_state" TEXT
                                )
                                """
            self.makeUpdateInsert(_sqlCreation)

    def getLastUndoIndex(self):
        """
            get the last undo index
        """
        _sqlCheck="select max(pycad_id) from pycadundo"
        _rows=self.makeSelect(_sqlCheck) 
        if _rows is None:            # no entity in the table
            _sqlInser="""INSERT INTO pycadundo (pycad_undo_state,pycad_ent_id) VALUES ("active",-1)"""# the -1 is like to say None
            self.makeUpdateInsert(_sqlInser)
            _rows=self.makeSelect(_sqlCheck) 
        if _rows== None:
            raise TypeError, "No row fatched in undo search "
        _row=_rows.fetchone()
        return _row[0] # get the max index of the table 

    def setActiveUndo(self,undoId):
        """
            set the active undo 
        """
        self.resetUndoTable()
        _sqlSetLastUndo="""update pycadundo set pycad_undo_state='active' where pycad_id='%s'"""%str(undoId)
        self.makeUpdateInsert(_sqlSetLastUndo)
        
    def resetUndoTable(self):
        """
            reset all the table value to no-value
        """
        _sqlReset="""update pycadundo set pycad_undo_state='no-value'"""
        self.makeUpdateInsert(_sqlReset)
    
    def getNextUndo(self,entId):
        """
            get the next undo index pycadundo 
        """
        self.resetUndoTable()
        _lastUndo=self.getLastUndoIndex()
        _sqlInser="""INSERT INTO pycadundo (pycad_undo_state,pycad_ent_id) VALUES ('active',%s)"""%str(entId)   
        self.makeUpdateInsert(_sqlInser)
        return self.getLastUndoIndex()

    def clearUndoTable(self):
        """
            Clear all the undo created 
        """
        _sqlDelete="""DELETE FROM pycadundo"""
        self.makeUpdateInsert(_sqlDelete)

    def getEntId(self,undoId):
        """
            Get The entity id corrisponding at the undoid
        """
        _sqlSelect="""SELECT pycad_ent_id FROM pycadundo WHERE pycad_id =%s"""%str(undoId)
        _rows=self.makeSelect(_sqlSelect)
        if _rows is not None:
            _row=_rows.fetchone()
            if _row is not None:
                return _row[0] 
        return None


def testUndo():
    print "*"*10
    _undo=PyCadUndoDb(None)
    print "getNextUndo"
    entityId=10
    _undo.getNextUndo(entityId)
    entityId=11
    _undo.getNextUndo(entityId)
    print "getLastUndoIndex"
    undoIndex=_undo.getLastUndoIndex()
    entityId=12
    _undo.getNextUndo(entityId)
    print "setActiveUndo"
    _undo.setActiveUndo(undoIndex)
    print "getEntId %s"%str(_undo.getEntId(entityId))
    print "resetUndoTable"
    #_undo.resetUndoTable()
    print "clearUndoTable" 
    #_undo.clearUndoTable()
