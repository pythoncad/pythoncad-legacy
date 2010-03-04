#!/usr/bin/env python

from pycadkernel import *

"""
TO BE TESTED:
    deleteEntity
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
    

def test():
    print "Create pycad object"
    kr=PyCadDbKernel()
    CreateModifieEntity(kr)
    
    
    #print "Add creation event"
    #kr.saveEntityEvent+=printId
    #testSinglePoint(kr)

    #print "Perform Undo"
    #kr.unDo()  
    #print "perform Undo"
    #kr.unDo()  
    #print "Perform Redo"
    #kr.reDo()


test()
def deleteTable(tableName):
    """
    delete the table name 
    """
    import sqlite3 as sql
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
    import sqlite3 as sql
    import cPickle 
    
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
        dumpDic=cPickle.dumps(dic)
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
    import sqlite3 as sql
    import cPickle 
    
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
        print "print Test with %s entitys"%str(i)
        testPointDb(i)
        testPointDb1(i)
