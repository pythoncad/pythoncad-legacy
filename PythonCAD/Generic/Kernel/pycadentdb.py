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

import cPickle as pickle

from Generic.Kernel.pycadent               import *
from Generic.Kernel.Entity.pycadstyle      import PyCadStyle
from Generic.Kernel.pycadbasedb            import PyCadBaseDb
from Generic.Kernel.pycadsettings          import PyCadSettings


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
                    pycad_entity_id INTEGER,
                    pycad_object_type TEXT,
                    pycad_object_definition TEXT,
                    pycad_style_id INTEGER,
                    pycad_security_id INTEGER,
                    pycad_undo_id INTEGER,
                    pycad_entity_state TEXT,
                    pycad_index NUMERIC,
                    pycad_visible INTEGER,
                    pycad_undo_visible INTEGER,
                    pycad_locked INTEGER,
                    pycad_bbox_xmin REAL,
                    pycad_bbox_ymin REAL,
                    pycad_bbox_xmax REAL,
                    pycad_bbox_ymax REAL)"""
            self.makeUpdateInsert(_sqlCreation)
        self.__revisionIndex=self.getRevisionIndex()
    
    def getRevisionIndex(self):
        """
            get the revision index from the database
        """
        _sql="""SELECT max(pycad_index) From pycadent"""
        index=self.fetchOneRow(_sql)
        if index is None: return 0
        return index
    def increaseRevisionIndex(self):
        """
            increase the relesed index
        """
        self.__revisionIndex+=1

    def decreseRevisionIndex(self):
        """
            decrese the revision index
        """
        self.__revisionIndex-=1

    def saveEntity(self,entityObj,undoId):
        """
            this method save the entity in the db
            entityObj = object that we whant to store
        """
        _entityId=entityObj.getId()
        _entityDump=pickle.dumps(entityObj.getConstructionElements())
        _entityType=entityObj.getEntityType()
        _entityVisible=entityObj.visible
        _styleId=entityObj.style
        _xMin,_yMin,_xMax,_yMax=entityObj.getBBox()
        _revisionIndex=self.__revisionIndex
        _revisionState=entityObj.state
        _sqlInsert="""INSERT INTO pycadent (
                    pycad_entity_id,
                    pycad_object_type,
                    pycad_object_definition,
                    pycad_style_id,
                    pycad_undo_id,
                    pycad_undo_visible,
                    pycad_bbox_xmin,
                    pycad_bbox_ymin,
                    pycad_bbox_xmax,
                    pycad_bbox_ymax,
                    pycad_entity_state,
                    pycad_index,
                    pycad_visible) VALUES
                    (%s,"%s","%s",%s,%s,1,"%s","%s",%s,%s,"%s",%s,%s)"""%(
                    str(_entityId),
                    str(_entityType),
                    str(_entityDump),
                    str(_styleId),
                    str(undoId),
                    str(_xMin),
                    str(_yMin),
                    str(_xMax),
                    str(_yMax), 
                    str(_revisionState),
                    str(_revisionIndex), 
                    str(_entityVisible))
        self.makeUpdateInsert(_sqlInsert)
        
    def getEntityFromTableId(self,entityTableId):
        """
            Get the entity object from the database Univoc id
        """
        _outObj=None
        _sqlGet="""SELECT   pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id,
                            pycad_entity_state,
                            pycad_index,
                            pycad_visible
                FROM pycadent
                WHERE pycad_id=%s"""%str(entityTableId)
        _rows=self.makeSelect(_sqlGet)
        if _rows is not None:
            _row=_rows.fetchone()
            if _row is not None:
                _style=str(_row[3])
                _dumpObj=pickle.loads(str(_row[2]))
                _outObj=PyCadEnt(_row[1],_dumpObj,_style,_row[0])
                _outObj.state=_row[4]
                _outObj.index=_row[5]
                _outObj.visible=_row[6]
                _outObj.updateBBox()
        return _outObj
    
    def getEntityEntityId(self,entityId):
        """
            get all the entity with the entity id
        """
        _outObj=None
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id,
                            pycad_entity_state,
                            pycad_index,
                            pycad_visible
                FROM pycadent
                WHERE pycad_entity_id=%s ORDER BY  pycad_id DESC"""%str(entityId)
        _dbEntRow=self.makeSelect(_sqlGet)
        if _dbEntRow is not None:
            _row=_dbEntRow.fetchone()
            _style=str(_row[4])
            _dumpObj=pickle.loads(str(_row[3]))
            _entObj=PyCadEnt(_row[2],_dumpObj,_style,_row[1])       
            _entObj.state=_row[5]
            _entObj.index=_row[6]
            _entObj.visible=_row[7]
            _entObj.updateBBox()
        return _entObj

    def getEntitysFromStyle(self,styleId):
        """
            return all the entity that match the styleId
        """
        _outObj=[]
        _sqlGet="""SELECT   pycad_id,
                            pycad_entity_id,
                            pycad_object_type,
                            pycad_object_definition,
                            pycad_style_id,
                            pycad_entity_state,
                            pycad_index,
                            pycad_visible
                    FROM pycadent
                    WHERE PyCad_Id IN (
                        SELECT max(PyCad_Id) 
                        FROM pycadent  
                        WHERE pycad_undo_visible=1 
                        GROUP BY pycad_entity_id ORDER BY PyCad_Id)
                    AND pycad_style_id=%s"""%str(styleId)
        _dbEntRow=self.makeSelect(_sqlCheck)
        for _row in _dbEntRow: 
            _style=_row[4]
            _dumpObj=pickle.loads(_row[3])
            _objEnt=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
            _objEnt.state=_row[5]
            _objEnt.index=_row[6]
            _objEnt.visible=_dbEntRow[7]
            _objEnt.updateBBox()            
            _outObj.append(_objEnt)
        return _outObj
    
    def _getEntInVersion(self, versionIndex):
        """
            get entity in version
        """
        #TODO: to be tested
        _sqlGet="""SELECT pycad_id,
                    pycad_entity_id,
                    pycad_object_type,
                    pycad_object_definition,
                    pycad_style_id,
                    pycad_entity_state,
                    pycad_index,
                    pycad_visible
                    FROM pycadent
                    WHERE PyCad_Id IN (
                        SELECT max(PyCad_Id) 
                        FROM pycadent  
                        WHERE pycad_undo_visible=1 
                        GROUP BY pycad_entity_id ORDER BY PyCad_Id)
                    AND pycad_entity_state NOT LIKE "DELETE"
                    AND pycad_index = %s
                    """%str(versionIndex)
        return self.makeSelect(_sqlGet)
        
    def getMultiFilteredEntity(self, visible=1, entityType='ALL'):
        """
            get all visible entity
        """  
        if entityType=='ALL':
            entityType="%"
        else:
            if not entityType in PY_CAD_ENT:
                raise TypeError,"Entity type %s not supported from the dbEnt"%str(entityType)  
        _sqlGet="""SELECT pycad_id,
                    pycad_entity_id,
                    pycad_object_type,
                    pycad_object_definition,
                    pycad_style_id,
                    pycad_entity_state,
                    pycad_index,
                    pycad_visible
                    FROM pycadent
                    WHERE PyCad_Id IN (
                        SELECT max(PyCad_Id) 
                        FROM pycadent  
                        WHERE pycad_undo_visible=1 
                        GROUP BY pycad_entity_id ORDER BY PyCad_Id)
                    AND pycad_entity_state NOT LIKE "DELETE"
                    AND pycad_visible =%s
                    AND pycad_object_type like '%s'
                    """%(str(visible), str(entityType))
        return self.makeSelect(_sqlGet)   
        
    def getEntityFromType(self,entityType):
        """
            get all the entity from a given type 
        """
        _outObj=[]
        _dbEntRow=self.getMultiFilteredEntity(entityType=entityType)
        for _row in _dbEntRow: 
            _style=_row[4]
            _dumpObj=pickle.loads(str(_row[3]))
            _objEnt=PyCadEnt(_row[2],_dumpObj,_style,_row[1])
            _objEnt.state=_row[5]
            _objEnt.index=_row[6]
            _objEnt.visible=_row[7]
            _objEnt.updateBBox()            
            _outObj.append(_objEnt)
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

    def markUndoVisibility(self,undoId,visible):
        """
            set as undo visible all the entity with undoId
        """
        _sqlVisible="""UPDATE pycadent SET pycad_undo_visible=%s
                    WHERE pycad_undo_id=%s"""%(str(visible),str(undoId))
        self.makeUpdateInsert(_sqlVisible)
    
    def markUndoVisibilityFromEntId(self, entityId, visible):
        """
            set the undo visibility to for all the entity
        """
        _sqlVisible="""UPDATE pycadent SET pycad_undo_visible=%s
                    WHERE pycad_entity_id=%s"""%(str(visible),str(entityId))
        try:
            self.makeUpdateInsert(_sqlVisible)
        except:
            # may be the update culd fail in case we create the first entity
            return

    def markEntVisibility(self,entId,visible):
        """
            mark the visibility of the entity
        """
        _tableId="""SELECT MAX(pycad_id) FROM pycadent 
                    WHERE pycad_entity_id=%s"""%str(entId)
        _entId=self.fetchOneRow(_tableId)
        if _entId is None:
            raise EmptyDbSelect, "Unable to find the entity with id %s"%str(entId)
        # Update the entity state
        _sqlVisible="""UPDATE pycadent SET pycad_undo_visible=%s
                    WHERE pycad_id=%s"""%(str(visible),str(_entId))
        self.makeUpdateInsert(_sqlVisible) 
             
    def hideAllEntityIstance(self,entId,visible):
        """
            hide all the row with entId
        """
        _sqlVisible="""UPDATE pycadent SET pycad_undo_visible=%s
                    WHERE pycad_entity_id=%s"""%(str(visible),str(entId))
        self.makeUpdateInsert(_sqlVisible)      
        
    def delete(self,tableId):
        """
            delete the entity from db
        """
        _sqlDelete="""DELETE FROM pycadent 
                        WHERE pycad_id=%s"""%str(tableId)
        self.makeUpdateInsert(_sqlDelete)
    
    def uptateEntity(self, entityObj):
        """
            Update an exsisting entity in the database 
            *************************Attention*********************************
            Remarks : using this function you will loose the undo history.
            Remarks : with this function you will force to update all the value
            so you can update value on released entity .
            Remarks : use this function only internaly at the kernel .
            *******************************************************************
        """    
        #toto : test update function
        _entityId=entityObj.getId()
        _entityDump=pickle.dumps(entityObj.getConstructionElements())
        _entityType=entityObj.getEntityType()
        _entityVisible=entityObj.visible
        _styleId=entityObj.style
        _xMin,_yMin,_xMax,_yMax=entityObj.getBBox()
        _revisionIndex=entityObj.index
        _revisionState=entityObj.state
        _sqlInsert="""UPDATE pycadent set (
                    pycad_object_type="%s",
                    pycad_object_definition="%s",
                    pycad_style_id=%s,
                    pycad_bbox_xmin=%s,
                    pycad_bbox_ymin=%s,
                    pycad_bbox_xmax=%s,
                    pycad_bbox_ymax=%s,
                    pycad_entity_state="%s",
                    pycad_index=%s,
                    pycad_visible=%s) 
                    WHERE PyCad_Id IN (
                        SELECT max(PyCad_Id) 
                        FROM pycadent  
                        WHERE pycad_undo_visible=1 
                        GROUP BY pycad_entity_id ORDER BY PyCad_Id) 
                    AND pycad_entity_id=%s
                    """%(
                    str(_entityType),
                    str(_entityDump),
                    str(_styleId),
                    str(_xMin),
                    str(_yMin),
                    str(_xMax),
                    str(_yMax), 
                    str(_revisionState),
                    str(_revisionIndex), 
                    str(_entityVisible), 
                    str(_entityId))
        self.makeUpdateInsert(_sqlInsert)
        
    def clearEnt(self):
        """
            perform the clear of all the entity that are not in the release state
        """
        _sql="""
                SELECT pycad_id 
                FROM pycadent
                WHERE pycad_entity_state NOT LIKE "RELEASED"
            """
        _rows=self.makeSelect(_sql)   
        for _row in _rows: 
            self.delete(_row[0])

def test():
    print "*"*10+" Start Test"
    dbEnt=PyCadEntDb(None)
    print "pyCadEntDb Created"
    style=PyCadStyle(1)
    print "PyCadStyle Created"
    ent=PyCadEnt('POINT',{'a':10},style,1)
    print "PyCadEnt Created"
    dbEnt.saveEntity(ent,1)
    print "PyCadEnt Saved"
    obj=dbEnt.getEntityEntityId(1)
    print "getEntity [%s]"%str(obj)
    for e in dbEnt.getEntityEntityId(1):
        print "Entity %s"%str(e)
    obj=dbEnt.getEntitysFromStyle
    for e in dbEnt.getEntityEntityId(1):
        print "Entity Style %s"%str(e)
    _newId=dbEnt.getNewEntId()
    print "New id %i"%(_newId)

    #to be tested 
    #markUndoVisibility
    #delete
    #getEntityFromType
