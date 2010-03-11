#!/usr/bin/env python

import sys
import os
import platform

pysqlite_path = None

# OSX specific path
if sys.platform == 'darwin':
    if platform.machine() == 'x86_64':
        # amd64
        pysqlite_path = os.path.join(os.getcwd(), 'darwin', 'lib64')
    else:
        # x86
        pysqlite_path = os.path.join(os.getcwd(), 'darwin', 'lib32')
# linux specific path
elif sys.platform == 'linux2':
    if platform.machine() == 'x86_64':
        # amd64
        pysqlite_path = os.path.join(os.getcwd(), 'linux2', 'lib64')
    else:
        # x86
        pysqlite_path = os.path.join(os.getcwd(), 'linux2', 'lib32')
# windows specific path  
elif sys.platform == 'win32':
    if platform.machine() == 'x86_64':
        # amd64
        pysqlite_path = os.path.join(os.getcwd(), 'win32', 'lib64')
    else:
        # x86
        pysqlite_path = os.path.join(os.getcwd(), 'win32', 'lib32')
    
# add pysqlite to search path
if pysqlite_path != None:
    sys.path.append(pysqlite_path)
    
# this is needed for me to use unpickle objects
sys.path.append(os.path.join(os.getcwd(), 'Generic', 'Kernel'))    
    
# check if it is possible to import pysqlite
try:
    from pysqlite2 import dbapi2 as sqlite
    print "R*Tree sqlite extention loaded"
except ImportError, e:
    print "Unable to load R*Tree sqlite extention"


from Generic.Kernel.pycadkernel import *

"""
TO BE TESTED:
    test events
"""

def printId(kernel,obj):
    """
        print the id of the obj
    """
    print "Save Entity: %s"%str(type(obj))
    
def testSinglePoint(kernel):
    """
        test single point operation
    """
    startTime=time.clock()
    print "Create a single point"
    basePoint=Point(10,1)
    print "singlePoint ",type(basePoint)
    kernel.saveEntity(basePoint)
    endTime=time.clock()-startTime
    print "Time for saving  a single point   %ss"%str(endTime)   
    
def testMultiPoints(kernel,nPoint)    :
    """
        test the point operatoin
    """
    startTime=time.clock()
    kernel.startMassiveCreation()
    for i in range(nPoint):
        basePoint=Point(10,i)
        kernel.saveEntity(basePoint)
    kernel.performCommit()
    endTime=time.clock()-startTime
    print "Create n: %s entity in : %ss"%(str(nPoint ),str(endTime))

def testMultiSegments(kernel,nSegments):
    """
        create a single segment
    """    
    startTime=time.clock()
    kernel.startMassiveCreation()
    for i in range(nSegments):
        _p1=Point(10,i)
        _p2=Point(10,i)
        _s=Segment(_p1,_p2)
        kernel.saveEntity(_s)
    kernel.performCommit()
    endTime=time.clock()-startTime
    print "Create n: %s entity in : %ss"%(str(nSegments ),str(endTime))
    
def testSingleSegment(kernel):
    """
        create a single segment
    """    
    _p1=Point(10,10)
    _p2=Point(10,20)
    _s=Segment(_p1,_p2)
    kernel.saveEntity(_s)

def testGetLayerEnt(kernel):
    """
        get layer dictionary of all the id child
    """
    startTime=time.clock()
    ids=kernel.getLayerChild('ROOT')
    nids=len(ids)
    endTime=time.clock()-startTime
    print "Get n: %s layer entity in : %ss"%(str(nids ),str(endTime))

def testPerformanceInCreation(kr):
    print "Points:"
    testMultiPoints(kr,1)
    #testMultiPoints(kr,10)
    #testMultiPoints(kr,100)
    #testMultiPoints(kr,1000)
    #testMultiPoints(kr,10000)
    #testMultiPoints(kr,100000)
    print "Segments:"
    testMultiSegments(kr,1)
    #testMultiSegments(kr,10)
    #testMultiSegments(kr,100)
    #testMultiSegments(kr,1000)
    #testMultiSegments(kr,10000)
    #testMultiSegments(kr,100000)
    testGetLayerEnt(kr)

def createSegment(kernel):
    """
        create a single segment
    """    
    _p1=Point(10,10)
    _p2=Point(10,20)
    _s=Segment(_p1,_p2)
    return kernel.saveEntity(_s)

def CreateModifieEntity(kr):
    """
        test for create and modifie an entity
    """
    ent=createSegment(kr)
    celement={'POINT_1':Point(100,100), 'POINT_2':Point(200,200)}
    ent.setConstructionElement(celement)
    kr.saveEntity(ent)
    




def deleteTable(tableName):
    """
    delete the table name 
    """
    #import sqlite3 as sql
    # sqlite + R*Tree module
    from pysqlite2 import dbapi2 as sql

    dbPath='pythoncad.pdr' 
    dbConnection = sql.connect(dbPath)
    statment="drop table pycadrel"
    _cursor = dbConnection.cursor()
    _rows = _cursor.execute(statment)
    dbConnection.commit()
    dbConnection.close()

def testPointDb(nLoop):
    """
    Test point creation 
    """
    #import sqlite3 as sql
    # sqlite + R*Tree module
    from pysqlite2 import dbapi2 as sql
    import cPickle as pickle
    
    dbConnection = sql.connect(":memory:")
    cursor=dbConnection.cursor()
    _sqlCreation="""CREATE TABLE pycadent(
                    pycad_id INTEGER PRIMARY KEY,
                    pycad_entity_id INTEGER,
                    pycad_object_type TEXT,
                    pycad_object_definition TEXT,
                    pycad_style_id INTEGER,
                    pycad_security_id INTEGER,
                    pycad_undo_id INTEGER,
                    pycad_entity_state TEXT,
                    pycad_date NUMERIC,
                    pycad_visible INTEGER,
                    pycad_undo_visible INTEGER,
                    pycad_locked INTEGER,
                    pycad_bbox_xmin REAL,
                    pycad_bbox_ymin REAL,
                    pycad_bbox_xmax REAL,
                    pycad_bbox_ymax REAL)"""
    cursor.execute(_sqlCreation)
    dic=[(x, y) for x in range(20) for y in range(1)]
    dbConnection.commit()
    startTime=time.clock()
    for i in range(nLoop):
        dumpDic=pickle.dumps(dic)
        sql="""insert into pycadent (pycad_entity_id,pycad_object_definition) values(1,"%s")"""%str(dumpDic)
        cursor.execute(sql)
    dbConnection.commit()
    endTime=time.clock()-startTime
    everage=endTime/nLoop
    print "End time for nLoop %s in %s everage %s "%(str(nLoop), str(endTime), str(everage))
    


def testPointDb1(nLoop):
    """
    Test point creation 
    """
    #import sqlite3 as sql
    # sqlite + R*Tree module
    from pysqlite2 import dbapi2 as sql
    import cPickle as pickle
    
    dbConnection = sql.connect(":memory:")
    cursor=dbConnection.cursor()
    _sqlCreation="""CREATE TABLE pycadent(
                    pycad_X REAL,
                    pycad_Y REAL)"""
    cursor.execute(_sqlCreation)
    dbConnection.commit()    
    dic=[(x,y) for x in range(20) for y in range(1)]
    startTime=time.clock()
    for i in range(nLoop):
        for x,y in dic:
            _sql="""INSERT INTO pycadent (pycad_X,pycad_Y) 
                VALUES (%s,%s)"""%(str(x),str(y))
            cursor.execute(_sql)
    dbConnection.commit()   
    endTime=time.clock()-startTime
    everage=endTime/nLoop
    print "End time for nLoop %s in %s everage %s "%(str(nLoop), str(endTime), str(everage))

def TestcPickleSql():
    for i in [10,100, 1000, 1000, 10000, 100000]:
        print ">>print Test with %s entitys"%str(i)
        testPointDb(i)
        testPointDb1(i)

def getAllSegment(kr):
    """
        get all the segments
    """
    print ">>Looking for segment"
    ent=kr.getEntityFromType('SEGMENT')
    for e in ent:
        print "e >>>>", e.eType




        
def test():
    print ">>Create pycad object"
    kr=PyCadDbKernel()
    #CreateModifieEntity(kr)
    #print "Add creation event"
    #kr.saveEntityEvent+=printId
    redo(kr)
    getAllSegment(kr)


class ioKernel(object):
    """
        This class provide a simple interface for using 
        PythonCad Kernel
    """
    def __init__(self):
        self.__kr=PyCadDbKernel()
        self.__command={}
        self.__command['H']=self.help
        self.__command['Esc']=self.endApplication
        self.__command['NewSegment']=self.newSegment
        self.__command['GetSegments']=self.getSegments
        self.__command['GetFromType']=self.getEntityFromType
        self.__command['UnDo']=self.unDo
        self.__command['ReDo']=self.reDo
        self.__command['Delete']=self.delete
        self.__command['Relese']=self.release
        self.__command['Hide']=self.hideEntity
        self.__command['UnHide']=self.unHideEntity
    def mainLoop(self):
        """
            mainLoop operation
        """
        while 1:
            imputstr=raw_input("Insert a command (H for Help)>> :")
            if self.__command.has_key(imputstr):
                self.__command[imputstr]()
            else:
                print "Wrong Command !!"
    def help(self):
        """
            print the help
        """
        print "*"*10
        print "PyCadIOInterface Help"
        for s in self.__command:
            print "command :" , s
        print "*"*10   
    def newSegment(self):
        """
            create a new segment
        """
        try:
            val=(raw_input("-->Get First Point (x,y) :"))
            p1=Point(val[0], val[1])
            val=(raw_input("-->Get Second Point (x,y) :"))
            p2=Point(val[0], val[1])
            _s=Segment(p1,p2)
            self.__kr.saveEntity(_s)
        except:
            print "---->Error on point creation !!"
    
    def getSegments(self):
        """
            return a list of all the segments
        """
        print "--<< Looking for segment"
        ent=self.__kr.getEntityFromType('SEGMENT')
        for e in ent:
            print "----<< Entity Type %s id %s "%(str(e.eType),str(e.getId()))

    def getEntityFromType(self):
        """
            get all the entity from the database
        """
        entType=raw_input("-->Insert the type you are looking for :")
        try:
            ent=self.__kr.getEntityFromType(entType)
            for e in ent:
                print "----<< Entity id : %s "%str(e.getId())
        except:
            print "----<<Err>>On Retryving entity type %s "%entType
            
    def reDo(self):
        """
            perform the redo command
        """
        try:
            print "-->>Perform Redo"
            self.__kr.reDo()  
        except UndoDb:
            print "----<<Err>>No more redo to performe"
    def unDo(self):
        """
            perform the undo command
        """
        try:
            print "-->>Perform unDo"
            self.__kr.unDo()  
        except UndoDb:
            print "----<<Err>>No more unDo to performe"
    def delete(self):
        """
            Delete the entity
        """
        try:
            val=(raw_input("-->Write entityId :"))
            self.__kr.deleteEntity(val)
        except:
            print "----<<Err>>Enable to delete the entity"

    def hideEntity(self):
        """
            hide an entity
        """
        entId=raw_input("-->Insert the id to hide :")
        try:
            self.__kr.hideEntity(entityId=entId)
        except:
            print "----<<Err>>On Hide the id : %s "%entId

    def unHideEntity(self):
        """
            unhide an entity
        """
        entId=raw_input("-->Insert the id to Unhide :")
        try:
            self.__kr.unHideEntity(entityId=entId)
        except:
            print "----<<Err>>On unHide the id : %s "%entId
        
    def endApplication(self):
        """
            close the application
        """
        sys.exit(0)
        
    def release(self):
        """
            release the current drawing
        """
        self.__kr.release()

if __name__=='__main__':
    #test()
    io=ioKernel()
    io.mainLoop()
    print "bye"


