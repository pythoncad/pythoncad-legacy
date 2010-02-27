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
    print "PrintId Event objId: %s"%str(obj.getId())
    
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
    print "start massive creation of point"
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
    print "start massive creation of Segments"
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
    
def test():
    print "Create pycad object"
    kr=PyCadDbKernel()
    print "Add creation event"
    #kr.saveEntityEvent+=printId
    #testSinglePoint(kr)
    #testMultiPoints(kr,1)
    #testSingleSegment(kr)
    #testMultiSegments(kr,1)
    #testMultiSegments(kr,10)
    #testMultiSegments(kr,100)
    #testMultiSegments(kr,1000)
    #testMultiSegments(kr,10000)
    #testMultiSegments(kr,100000)
    
    #print "Perform Undo"
    #kr.unDo()  
    #print "perform Undo"
    #kr.unDo()  
    #print "Perform Redo"
    #kr.reDo()
    
test()
