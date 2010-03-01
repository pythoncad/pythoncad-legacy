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
    
def test():
    print "Create pycad object"
    kr=PyCadDbKernel()
    #print "Add creation event"
    #kr.saveEntityEvent+=printId
    #testSinglePoint(kr)
    #testMultiPoints(kr,1)
    #testMultiPoints(kr,10)
    #testMultiPoints(kr,100)
    #testMultiPoints(kr,1000)
    #testMultiPoints(kr,10000)
    #testMultiPoints(kr,100000)
    #testSingleSegment(kr)
    #testMultiSegments(kr,1)
    #testMultiSegments(kr,10)
    #testMultiSegments(kr,100)
    #testMultiSegments(kr,1000)
    #testMultiSegments(kr,10000)
    #testMultiSegments(kr,100000)
    testGetLayerEnt(kr)
    #print "Perform Undo"
    #kr.unDo()  
    #print "perform Undo"
    #kr.unDo()  
    #print "Perform Redo"
    #kr.reDo()
    
test()
