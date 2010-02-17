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
# This module provide basic operation for the entity in the pythoncad database
#

import cPickle


from pycadbasedb import PyCadBaseDb
from pycadent       import PyCadEnt
from pycadstyle     import PyCadStyle
 
class PyCadEntDb(PyCadBaseDb):
    """
        this class provide the besic operation for the entity
    """
    def __init__(self,dbConnection):
        PyCadBaseDb.__init__(self)
        if dbConnection is None:
            self.createConnection()
        else:
            self.setConnection(dbConnection)

        _sqlCheck="""select * from sqlite_master where name like 'pycadent'"""
        _table=self.makeSelect(_sqlCheck).fetchone()
        if _table is None:
            _sqlCreation="""CREATE TABLE pycadent(
                    pycad_id INTEGER PRIMARY KEY,
                    pycad_entity_id NUMERIC,
                    pycad_object_type TEXT,
                    pycad_object_definition TEXT,
                    pycad_style_id INTEGER,
                    pycad_security_id INTEGER,
                    pycad_locked INTEGER)"""
            self.makeUpdateInsert(_sqlCreation)
            
    def saveEntity(self,entityObj):
        """
            this method save the entity in the db
            entityObj = object that we whant to store
        """
        _entityId=entityObj.getId()
        _entityDump=cPickle.dumps(entityObj.getConstructionPoint())
        _entityType=entityObj.getEntityType()
        _styleId=entityObj.getStyle().getId()
        _sqlInsert="""INSERT INTO pycadent (
                    pycad_entity_id,
                    pycad_object_type,
                    pycad_object_definition,
                    pycad_style_id) VALUES
                    (%s,"%s","%s",%s)"""%(str(_entityId),str(_entityType),str(_entityDump),str(_styleId))
        self.makeUpdateInsert(_sqlInsert)
        
    def getEntity(self,entityTableId):
        """
            Get the entity object from the database Univoc id
        """
        _outObj=None
        _sqlGet="""SELECT   pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_id=%s"""%str(entityTableId)
        _rows=self.makeSelect(_sqlGet)
        if _rows is not None:
            _dbEntRow=_rows.fetchone()
            if _dbEntRow is not None:
                _style=str(_dbEntRow[3])
                _dumpObj=cPickle.loads(str(_dbEntRow[2]))
                _outObj=PyCadEnt(_dbEntRow[1],_dumpObj,_style,_dbEntRow[0])
        return _outObj
    
    def getEntitys(self,entityId):
        """
            get all the entity with the entity id
            remarcs:
            this method return all the history of the entity
        """
        _outObj={}
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_entity_id=%s ORDER BY pycad_id"""%str(entityId)
        _dbEntRow=self.makeSelect(_sqlGet)
        if _dbEntRow is not None:
            for _row in _dbEntRow: 
                _style=str(_row[4])
                _dumpObj=cPickle.loads(str(_row[3]))
                _outObj[_row[0]]=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
        return _outObj

    def getEntitysFromStyle(self,styleId):
        """
            return all the entity that match the styleId
        """
        _outObj={}
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id
                FROM pycadent
                WHERE pycad_style_id=%s ORDER BY pycad_id"""%str(styleId)
        _dbEntRow=self.makeSelect(_sqlCheck)
        for _row in _dbEntRow: 
            _style=_row[4]
            _dumpObj=cPickle.loads(_row[3])
            _outObj[_row[0]]=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
        return _outObj
    
    def getNewEntId(self):
        """
            get the last id entity 
        """
        _outObj=0
        _sqlSelect="""select max(pycad_entity_id) from pycadent"""
        _rows=self.makeSelect(_sqlSelect)
        if _rows is not None:
            _dbEntRow=_rows.fetchone()
            if _dbEntRow is not None:
                if _dbEntRow[0] is not None:
                    _outObj=int(_dbEntRow[0])
        return _outObj
    
def test():
    print "*"*10+" Start Test"
    dbEnt=PyCadEntDb(None)
    print "pyCadEntDb Created"
    style=PyCadStyle(1)
    print "PyCadStyle Created"
    ent=PyCadEnt('POINT',{'a':10},style,1)
    print "PyCadEnt Created"
    dbEnt.saveEntity(ent)
    print "PyCadEnt Saved"
    obj=dbEnt.getEntity(1)
    print "getEntity [%s]"%str(obj)
    for e in dbEnt.getEntitys(1):
        print "Entity %s"%str(e)
    obj=dbEnt.getEntitysFromStyle
    for e in dbEnt.getEntitys(1):
        print "Entity Style %s"%str(e)
    _newId=dbEnt.getNewEntId()
    print "New id %i"%(_newId)

