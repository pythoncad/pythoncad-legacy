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
# This module provide basic operation for the Relation in the pythoncad database
#

import cPickle

from pycadent       import PyCadEnt
from pycadbasedb    import PyCadBaseDb

class PyCadRelDb(PyCadBaseDb):
    """
        this class provide the besic operation for the relation
    """
    def __init__(self,dbConnection=None):
        PyCadBaseDb.__init__(self)
        if dbConnection is None:
            self.createConnection()
        else:
            self.setConnection(dbConnection)

        _sqlCheck="""select * from sqlite_master where name like 'pycadrel'"""
        _table=self.makeSelect(_sqlCheck).fetchone()
        if _table is None:
            _sqlCreation="""CREATE TABLE pycadrel(
                    "pycad_id" INTEGER PRIMARY KEY,
                    "pycad_parent_id" INTEGER,
                    "pycad_child_id" INTEGER
                    )"""
            self.makeUpdateInsert(_sqlCreation)
            
    def saveRelation(self,parentEntObj,childEntObj):
        """
            This method save the Relation in the db
        """
        _parentEntityId=parentEntObj.getId()
        _childEntityId=childEntObj.getId()
        _sqlInsert="""INSERT INTO pycadrel (
                      pycad_parent_id,
                      pycad_child_id
                      ) VALUES
                      (%s,"%s")"""%(
                    str(_parentEntityId),
                    str(_childEntityId))
        self.makeUpdateInsert(_sqlInsert)
        
    def getChildrenIds(self,entityParentId):
        """
            Get the children id of a relation
        """
        _outObj=[]
        _sqlGet="""SELECT pycad_child_id
                FROM pycadrel
                WHERE pycad_parent_id=%s"""%str(entityParentId)
        _rows=self.makeSelect(_sqlGet)
        _dbEntRow=self.makeSelect(_sqlGet)
        if _dbEntRow is not None:
            for _row in _dbEntRow: 
                _outObj.append(_row[0])
        return _outObj
     
    def deleteFromParent(self,entityObj):
        """
            Delete the entity from db
        """
        _entityId=entityObj.getId()
        _sqlDelete="""DELETE FROM pycadrel 
            WHERE pycad_parent_id='%s'"""%str(_entityId)
        self.makeUpdateInsert(_sqlDelete)
        
    def deleteFromChild(self,entityObj):
        """
            Delete the entity from db
        """
        _entityId=entityObj.getId()
        _sqlDelete="""DELETE FROM pycadrel 
            WHERE pycad_child_id='%s'"""%str(_entityId)
        self.makeUpdateInsert(_sqlDelete)

    def deleteRelation(self,entityObjParent,entityObjChild):
        """
            delete the relation from parent and child
        """
        _parentId=entityObjParent.getId()
        _childId=entityObjChild.getId()
        _sqlDelete="""DELETE FROM pycadrel 
            WHERE pycad_parent_id='%s' and pycad_child_id='%s'and """%(str(_parentId),str(_childId))
        self.makeUpdateInsert(_sqlDelete)

        
""" TODO:

"""
def test():
    from pycadent       import PyCadEnt
    from pycadstyle import PyCadStyle
    print "*"*10+" Start Test"
    _pcr=PyCadRelDb()
    _style=PyCadStyle(1)
    _e1=PyCadEnt("POINT",{},_style,10)
    for i in range(5):
        _e2=PyCadEnt("POINT",{},_style,i)
        _pcr.saveRelation(_e1,_e2)
    for i in _pcr.getChildrenIds(10):
        print "cildid %s "%str(i)
    print "perform delete"
    _pcr.deleteFromParent(_e1)

"""
    TOBE TESTED:
    deleteFromChild
    deleteRelation
"""
