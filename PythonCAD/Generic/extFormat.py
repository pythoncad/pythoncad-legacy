#
# Copyright (c) 2009 Matteo Boscolo
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the termscl_bo of the GNU General Public License as published by
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
#
# This code is written by Yagnesh Desai
#

dxfDebug=False

import os.path
import math # added to handle arc start and end point defination
import re # added to handle Mtext


from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.layer import Layer
from PythonCAD.Interface.Gtk import gtkdialog as gtkDialog
from PythonCAD.Generic.text import *
from PythonCAD.Generic import util

changecolor = {
'#000000':0, 0:'#000000',
'#ff0000':1, 1:'#ff0000',
'#ffff00':2, 2:'#ffff00',
'#00ff00':3, 3:'#00ff00',
'#00ffff':4, 4:'#00ffff',
'#0000ff':5, 5:'#0000ff',
'#ff00ff':6, 6:'#ff00ff',
'#ffffff':7, 7:'#ffffff',
'#414141':8, 8:'#414141',
'#808080':9, 9:'#808080',
'#ff0000':10, 10:'#ff0000',
'#ffaaaa':11, 11:'#ffaaaa',
'#bd0000':12, 12:'#bd0000',
'#bd7e7e':13, 13:'#bd7e7e',
'#810000':14, 14:'#810000',
'#815656':15, 15:'#815656',
'#680000':16, 16:'#680000',
'#684545':17, 17:'#684545',
'#4f0000':18, 18:'#4f0000',
'#4f3535':19, 19:'#4f3535',
'#ff3f00':20, 20:'#ff3f00',
'#ffbfaa':21, 21:'#ffbfaa',
'#bd2e00':22, 22:'#bd2e00',
'#bd8d7e':23, 23:'#bd8d7e',
'#811f00':24, 24:'#811f00',
'#816056':25, 25:'#816056',
'#681900':26, 26:'#681900',
'#684e45':27, 27:'#684e45',
'#4f1300':28, 28:'#4f1300',
'#4f3b35':29, 29:'#4f3b35',
'#ff7f00':30, 30:'#ff7f00',
'#ffd4aa':31, 31:'#ffd4aa',
'#bd5e00':32, 32:'#bd5e00',
'#bd9d7e':33, 33:'#bd9d7e',
'#814000':34, 34:'#814000',
'#816b56':35, 35:'#816b56',
'#683400':36, 36:'#683400',
'#685645':37, 37:'#685645',
'#4f2700':38, 38:'#4f2700',
'#4f4235':39, 39:'#4f4235',
'#ffbf00':40, 40:'#ffbf00',
'#ffeaaa':41, 41:'#ffeaaa',
'#bd8d00':42, 42:'#bd8d00',
'#bdad7e':43, 43:'#bdad7e',
'#816000':44, 44:'#816000',
'#817656':45, 45:'#817656',
'#684e00':46, 46:'#684e00',
'#685f45':47, 47:'#685f45',
'#4f3b00':48, 48:'#4f3b00',
'#4f4935':49, 49:'#4f4935',
'#ffff00':50, 50:'#ffff00',
'#ffffaa':51, 51:'#ffffaa',
'#bdbd00':52, 52:'#bdbd00',
'#bdbd7e':53, 53:'#bdbd7e',
'#818100':54, 54:'#818100',
'#818156':55, 55:'#818156',
'#686800':56, 56:'#686800',
'#686845':57, 57:'#686845',
'#4f4f00':58, 58:'#4f4f00',
'#4f4f35':59, 59:'#4f4f35',
'#bfff00':60, 60:'#bfff00',
'#eaffaa':61, 61:'#eaffaa',
'#8dbd00':62, 62:'#8dbd00',
'#adbd7e':63, 63:'#adbd7e',
'#608100':64, 64:'#608100',
'#768156':65, 65:'#768156',
'#4e6800':66, 66:'#4e6800',
'#5f6845':67, 67:'#5f6845',
'#3b4f00':68, 68:'#3b4f00',
'#494f35':69, 69:'#494f35',
'#7fff00':70, 70:'#7fff00',
'#d4ffaa':71, 71:'#d4ffaa',
'#5ebd00':72, 72:'#5ebd00',
'#9dbd7e':73, 73:'#9dbd7e',
'#408100':74, 74:'#408100',
'#6b8156':75, 75:'#6b8156',
'#346800':76, 76:'#346800',
'#566845':77, 77:'#566845',
'#274f00':78, 78:'#274f00',
'#424f35':79, 79:'#424f35',
'#3fff00':80, 80:'#3fff00',
'#bfffaa':81, 81:'#bfffaa',
'#2ebd00':82, 82:'#2ebd00',
'#8dbd7e':83, 83:'#8dbd7e',
'#1f8100':84, 84:'#1f8100',
'#608156':85, 85:'#608156',
'#196800':86, 86:'#196800',
'#4e6845':87, 87:'#4e6845',
'#134f00':88, 88:'#134f00',
'#3b4f35':89, 89:'#3b4f35',
'#00ff00':90, 90:'#00ff00',
'#aaffaa':91, 91:'#aaffaa',
'#00bd00':92, 92:'#00bd00',
'#7ebd7e':93, 93:'#7ebd7e',
'#008100':94, 94:'#008100',
'#568156':95, 95:'#568156',
'#006800':96, 96:'#006800',
'#456845':97, 97:'#456845',
'#004f00':98, 98:'#004f00',
'#354f35':99, 99:'#354f35',
'#00ff3f':100, 100:'#00ff3f',
'#aaffbf':101, 101:'#aaffbf',
'#00bd2e':102, 102:'#00bd2e',
'#7ebd8d':103, 103:'#7ebd8d',
'#00811f':104, 104:'#00811f',
'#568160':105, 105:'#568160',
'#006819':106, 106:'#006819',
'#45684e':107, 107:'#45684e',
'#004f13':108, 108:'#004f13',
'#354f3b':109, 109:'#354f3b',
'#00ff7f':110, 110:'#00ff7f',
'#aaffd4':111, 111:'#aaffd4',
'#00bd5e':112, 112:'#00bd5e',
'#7ebd9d':113, 113:'#7ebd9d',
'#008140':114, 114:'#008140',
'#56816b':115, 115:'#56816b',
'#006834':116, 116:'#006834',
'#456856':117, 117:'#456856',
'#004f27':118, 118:'#004f27',
'#354f42':119, 119:'#354f42',
'#00ffbf':120, 120:'#00ffbf',
'#aaffea':121, 121:'#aaffea',
'#00bd8d':122, 122:'#00bd8d',
'#7ebdad':123, 123:'#7ebdad',
'#008160':124, 124:'#008160',
'#568176':125, 125:'#568176',
'#00684e':126, 126:'#00684e',
'#45685f':127, 127:'#45685f',
'#004f3b':128, 128:'#004f3b',
'#354f49':129, 129:'#354f49',
'#00ffff':130, 130:'#00ffff',
'#aaffff':131, 131:'#aaffff',
'#00bdbd':132, 132:'#00bdbd',
'#7ebdbd':133, 133:'#7ebdbd',
'#008181':134, 134:'#008181',
'#568181':135, 135:'#568181',
'#006868':136, 136:'#006868',
'#456868':137, 137:'#456868',
'#004f4f':138, 138:'#004f4f',
'#354f4f':139, 139:'#354f4f',
'#00bfff':140, 140:'#00bfff',
'#aaeaff':141, 141:'#aaeaff',
'#008dbd':142, 142:'#008dbd',
'#7eadbd':143, 143:'#7eadbd',
'#006081':144, 144:'#006081',
'#567681':145, 145:'#567681',
'#004e68':146, 146:'#004e68',
'#455f68':147, 147:'#455f68',
'#003b4f':148, 148:'#003b4f',
'#35494f':149, 149:'#35494f',
'#007fff':150, 150:'#007fff',
'#aad4ff':151, 151:'#aad4ff',
'#005ebd':152, 152:'#005ebd',
'#7e9dbd':153, 153:'#7e9dbd',
'#004081':154, 154:'#004081',
'#566b81':155, 155:'#566b81',
'#003468':156, 156:'#003468',
'#455668':157, 157:'#455668',
'#00274f':158, 158:'#00274f',
'#35424f':159, 159:'#35424f',
'#003fff':160, 160:'#003fff',
'#aabfff':161, 161:'#aabfff',
'#002ebd':162, 162:'#002ebd',
'#7e8dbd':163, 163:'#7e8dbd',
'#001f81':164, 164:'#001f81',
'#566081':165, 165:'#566081',
'#001968':166, 166:'#001968',
'#454e68':167, 167:'#454e68',
'#00134f':168, 168:'#00134f',
'#353b4f':169, 169:'#353b4f',
'#0000ff':170, 170:'#0000ff',
'#aaaaff':171, 171:'#aaaaff',
'#0000bd':172, 172:'#0000bd',
'#7e7ebd':173, 173:'#7e7ebd',
'#000081':174, 174:'#000081',
'#565681':175, 175:'#565681',
'#000068':176, 176:'#000068',
'#454568':177, 177:'#454568',
'#00004f':178, 178:'#00004f',
'#35354f':179, 179:'#35354f',
'#3f00ff':180, 180:'#3f00ff',
'#bfaaff':181, 181:'#bfaaff',
'#2e00bd':182, 182:'#2e00bd',
'#8d7ebd':183, 183:'#8d7ebd',
'#1f0081':184, 184:'#1f0081',
'#605681':185, 185:'#605681',
'#190068':186, 186:'#190068',
'#4e4568':187, 187:'#4e4568',
'#13004f':188, 188:'#13004f',
'#3b354f':189, 189:'#3b354f',
'#7f00ff':190, 190:'#7f00ff',
'#d4aaff':191, 191:'#d4aaff',
'#5e00bd':192, 192:'#5e00bd',
'#9d7ebd':193, 193:'#9d7ebd',
'#400081':194, 194:'#400081',
'#6b5681':195, 195:'#6b5681',
'#340068':196, 196:'#340068',
'#564568':197, 197:'#564568',
'#27004f':198, 198:'#27004f',
'#42354f':199, 199:'#42354f',
'#bf00ff':200, 200:'#bf00ff',
'#eaaaff':201, 201:'#eaaaff',
'#8d00bd':202, 202:'#8d00bd',
'#ad7ebd':203, 203:'#ad7ebd',
'#600081':204, 204:'#600081',
'#765681':205, 205:'#765681',
'#4e0068':206, 206:'#4e0068',
'#5f4568':207, 207:'#5f4568',
'#3b004f':208, 208:'#3b004f',
'#49354f':209, 209:'#49354f',
'#ff00ff':210, 210:'#ff00ff',
'#ffaaff':211, 211:'#ffaaff',
'#bd00bd':212, 212:'#bd00bd',
'#bd7ebd':213, 213:'#bd7ebd',
'#810081':214, 214:'#810081',
'#815681':215, 215:'#815681',
'#680068':216, 216:'#680068',
'#684568':217, 217:'#684568',
'#4f004f':218, 218:'#4f004f',
'#4f354f':219, 219:'#4f354f',
'#ff00bf':220, 220:'#ff00bf',
'#ffaaea':221, 221:'#ffaaea',
'#bd008d':222, 222:'#bd008d',
'#bd7ead':223, 223:'#bd7ead',
'#810060':224, 224:'#810060',
'#815676':225, 225:'#815676',
'#68004e':226, 226:'#68004e',
'#68455f':227, 227:'#68455f',
'#4f003b':228, 228:'#4f003b',
'#4f3549':229, 229:'#4f3549',
'#ff007f':230, 230:'#ff007f',
'#ffaad4':231, 231:'#ffaad4',
'#bd005e':232, 232:'#bd005e',
'#bd7e9d':233, 233:'#bd7e9d',
'#810040':234, 234:'#810040',
'#81566b':235, 235:'#81566b',
'#680034':236, 236:'#680034',
'#684556':237, 237:'#684556',
'#4f0027':238, 238:'#4f0027',
'#4f3542':239, 239:'#4f3542',
'#ff003f':240, 240:'#ff003f',
'#ffaabf':241, 241:'#ffaabf',
'#bd002e':242, 242:'#bd002e',
'#bd7e8d':243, 243:'#bd7e8d',
'#81001f':244, 244:'#81001f',
'#815660':245, 245:'#815660',
'#680019':246, 246:'#680019',
'#68454e':247, 247:'#68454e',
'#4f0013':248, 248:'#4f0013',
'#4f353b':249, 249:'#4f353b',
'#333333':250, 250:'#333333',
'#505050':251, 251:'#505050',
'#696969':252, 252:'#696969',
'#828282':253, 253:'#828282',
'#bebebe':254, 254:'#bebebe',
'#ffffff':255, 255:'#ffffff',
}


class ExtFormat(object):
    """
        This class provide base class for hendly different drawing format in pythoncad
    """
    def __init__(self,gtkimage):
        """
            Default Constructor
        """
        self.__gtkimage=gtkimage
 
    def openFile(self,fileName):
        """
           Open a generic file 
        """
        path,exte=os.path.splitext( fileName )
        if( exte.upper()==".dxf".upper()):
            dxf=Dxf(self.__gtkimage,fileName)
            dxf.importEntitis()
            self.__gtkimage.fitImage()            
            if not dxf.getError() is None:
                gtkDialog.reportDialog(self.__gtkimage,"Report On ImportFile",dxf.getError())
            
    def saveFile(self,fileName):
        """
            save the current file in a non pythoncad Format
        """
        path,exte=os.path.splitext( fileName )
        if( exte.upper()==".dxf".upper()):
            dxf=Dxf(self.__gtkimage,fileName)
            dxf.exportEntitis()

class DrawingFile(object):
    """
        This Class provide base capability to read write a  file
    """
    def __init__(self,fileName):
        """
            Base Constructor
        """
        dPrint( "Debug: DrawingFile constructor")
        self.__fn=fileName
        self.__fb=None
        self.__errors=[]
        self.__reading=False
        self.__writing=False        
        self.__lineNumber=0
        
    def readAsci(self):
        """
            Read a generic file 
        """
        dPrint("Debug: Read asci File")
        self.__fb=open(self.__fn,'r')
        self.__reading=True
        self.__writing=False
        
    def createAsci(self):
        """
            create the new file 
        """
        self.__fb=open(self.__fn,'w')
        self.__reading=False
        self.__writing=True
        
    def fileObject(self):
        """
            Return the file opened 
        """
        dPrint( "Debug: GetFileObject")
        if self.__fb is not None: 
          dPrint( "Debug: Return file object")
          return self.__fb
        else: 
          dPrint( "Debug: None")
          return None
    
    def readLine(self):
        """
            read a line and return it
        """
        if self.__reading:
            self.__lineNumber=self.__lineNumber+1
            return self.__fb.readline()
        else:
            raise "Unable to perfor reading operation"
    
    def writeLine(self,line):
        """
            write a line to the file
        """
        if self.__writing:
            self.__fb.write(line)
        else:
            raise "Unable to perfor writing operation"
        
    def writeError(self,functionName,msg):
        """
            Add an Error to the Collection
        """
        _msg=u'Error on line %s function Name: %s Message %s \n'%(
            str(self.__lineNumber),functionName,msg)
        self.__errors.append(_msg)
        
    def getError(self):
        """
        get the import export error
        """
        if len(self.__errors)>0:
            return self.__errors
        else: 
            return None
    def close(self):
        """
        close the active fileObject
        """
        if not self.__fb is None:
            self.__fb.close()
    def getFileName(self):
        """
            Return The active file Name
        """
        return self.__fn
    
class Dxf(DrawingFile):
    """
        this class provide dxf reading/writing capability 
    """
    def __init__(self,gtkimage,fileName):
        """
            Default Constructor
        """
        dPrint( "Debug: Dxf constructor")
        DrawingFile.__init__(self,fileName)
        self.__gtkimage=gtkimage
        self.__image=gtkimage.getImage()
        self.__dxfLayer=None
        
    def exportEntitis(self):
        """
            export The current file in dxf format
        """
        _fo=self.createAsci()               #open the file for writing
        _layersEnts=self.getAllEntitis()    #get all the entities from the file
        self.writeLine("999\nExported from Pythoncad\nSECTION\n  2\nENTITIES\n")#header section for entities
        for _key in _layersEnts:            #Looping at all layer
            #create header section#
            for _obj in _layersEnts[_key]:  #looping at all entities in the layer
                if isinstance(_obj,Segment):#if it's segment 
                    self.writeSegment(_obj) # ad it at the dxf drawing
                if isinstance(_obj,Circle):
                    self.writeCircle(_obj)
                if isinstance(_obj,Arc):
                    self.writeArc(_obj)
                if isinstance(_obj,Polyline):
                    self.writePolyline(_obj)
                if isinstance(_obj,TextBlock):
                    self.writeText(_obj)
                # go on end implements the other case arc circle ...
        self.writeLine("  0\nENDSEC\n  0\nEOF")#writing End Of File
        self.close()
        
    def getAllEntitis(self):
        """
            retrive all the entitys from the drawing 
        """
        _outLayers={}
        _layers = [self.__image.getActiveLayer()]
        while len(_layers):
            _layerEnts=[]
            _layer = _layers.pop()
            _layerName=_layer.getName()            
            _objs=_layer.getAllEntitys()
            for _o in _objs:
                _layerEnts.append(_o)
            _outLayers[_layerName]=_layerEnts
        return _outLayers
    
    def writeSegment(self,e):
        """
           write segment to the dxf file 
        """
        x1,y1=e.getP1().getCoords()
        x2,y2=e.getP2().getCoords()
        _c = e.getColor()
        _c = str(_c)
        _c = changecolor[_c]
        dPrint("debug line color are %s"%str( _c))
        self.writeLine("  0\nLINE\n100\nAcdbLine\n")
        self.writeLine(" 62\n" + str(_c) +"\n")
        self.writeLine(" 10\n" +str(x1) +"\n")
        self.writeLine(" 20\n" +str(y1) +"\n 30\n0.0\n")
        self.writeLine(" 11\n" +str(x2) +"\n")
        self.writeLine(" 21\n" +str(y2) +"\n 31\n0.0\n") 

    def writeCircle(self,e):
        """
           Write Circle to the dxf file
        """
        x1,y1=e.getCenter().getCoords()
        r=e.getRadius()
        _c = e.getColor()
        _c = str(_c)
        _c = changecolor[_c]
        dPrint(" circle color are %s"%str(_c))
        self.writeLine("  0\nCIRCLE\n100\nAcDbCircle\n")
        self.writeLine(" 62\n" +str(_c) +"\n")
        self.writeLine(" 10\n" +str(x1) +"\n")
        self.writeLine(" 20\n" +str(y1) +"\n 30\n0.0\n")
        self.writeLine(" 40\n" +str(r) +"\n")
    def writeArc(self,e):
        """
           Write Arc to the dxf file
        """
        x1,y1 = e.getCenter().getCoords()
        r = e.getRadius()
        sa = e.getStartAngle()
        ea = e.getEndAngle()
        _c = e.getColor()
        _c = str(_c)
        _c = changecolor[_c]
        print "debug Arc color are", _c
        self.writeLine("  0\nARC\n100\nAcDbCircle\n")
        self.writeLine(" 62\n" +str(_c) +"\n")
        self.writeLine(" 10\n" +str(x1) +"\n")
        self.writeLine(" 20\n" +str(y1) +"\n 30\n0.0\n")
        self.writeLine(" 40\n" +str(r) +"\n")
        self.writeLine(" 50\n" +str(sa) +"\n 51\n"+str(ea)+"\n")
    def writePolyline(self,e):
        """
           Write Polyline to the dxf file
        """
        _c = e.getColor()
        _c = str(_c)
        _c = changecolor[_c]
        print "debug Arc color are", _c
        self.writeLine("  0\nLWPOLYLINE\n100\nAcDbPolyline\n")
        self.writeLine(" 62\n" +str(_c) +"\n")
        count = e.getNumPoints()
        self.writeLine(" 90\n" +str(count)+ "\n")
        self.writeLine(" 70\n0\n")
        self.writeLine(" 43\n0\n")
        c = 0
        points = []
        while c < count:
            x1,y1 = e.getPoint(c).getCoords()
            self.writeLine(" 10\n" +str(x1) +"\n")
            self.writeLine(" 20\n" +str(y1) +"\n")
            c = c + 1
    def writeText(self,e):
        """
           Write Text to the dxf file
        """
        x1,y1=e.getLocation()
        h = e.getSize()
        _c = e.getColor()
        _c = str(_c)
        _c = changecolor[_c]
        print "debug Text color are", _c
        txt = e.getText()
        txt = txt.replace(' ', '\~')
        txt = txt.replace('\n', '\P')
        self.writeLine("  0\nMTEXT\n100\nAcDbMText\n")
        self.writeLine(" 62\n" +str(_c) +"\n")
        self.writeLine(" 10\n" +str(x1) +"\n")
        self.writeLine(" 20\n" +str(y1) +"\n 30\n0.0\n")
        self.writeLine(" 40\n" +str(h) +"\n")
        self.writeLine("  1\n" +str(txt) +"\n")
    def importEntitis(self):
        """
            Open The file and create The entity in pythonCad
        """
        dPrint( "Debug: import entitys")
        self.readAsci();
        _layerName,_ext=os.path.splitext(os.path.basename(self.getFileName()))
        _layerName="Imported_"+_layerName
        _dxfLayer=Layer(_layerName)
        self.__image.addLayer(_dxfLayer)
        self.__dxfLayer=_dxfLayer 
        while True:
            _k = self.readLine()
            if not _k: break
            else:
                dPrint( "Debug: Read Line line = [%s]"%str(_k))
                if _k[0:5] == 'TABLE':
                    self.readTable()
                    continue
                if _k[0:4] == 'LINE':
                    self.createLineFromDxf()
                    continue
                if _k[0:6] == 'CIRCLE':
                    self.createCircleFromDxf()
                    continue
                if _k[0:5] == 'MTEXT':
                    self.createTextFromDxf()
                    continue
                if _k[0:4] == 'TEXT':
                    self.createTextFromDxf()
                    continue
                if _k[0:3] == 'ARC':
                    self.createArcFromDxf()
                    continue
                if _k[0:10] == 'LWPOLYLINE':
                    self.createPolylineFromDxf()
                    continue
                if _k[0:8] == 'POLYLINE':
                    self.createPolylineFromDxf()
                    continue
                if not _k : break
    def readTable(self):
        """
        Reading the data in the dxf file under TABLE section
        it collects the information regarding the
        Layers, Colors and Linetype 
        WORK IN PROGRESS
        """
        print 'debug table found !'
        layerData = {}
        dxfColor = 0
        layerName = '0'
        _k = self.readLine()
        if _k[0:3] == '  2':
            _k = self.readLine()
            if _k[0:5] != 'LAYER':
                pass
            while True:
                _k = self.readLine()
                if _k[0:6] == 'ENDTAB':
                    break
                if _k[0:3] == '  2':
                    _k = self.readLine()
                    layerName = _k
                    print "Debug New LayerName=", layerName
                if _k[0:3] == ' 62':
                    _k = self.readLine()
                    dxfColor = _k
                    print "Debug new dxfColor = ", dxfColor
                layerData[layerName] = dxfColor
        print "Debug layerData", layerData
            
    def createLineFromDxf(self):
        """
            read the line dxf section and create the line
        """
        dPrint( "Debug createLineFromDxf" )
        x1 = None
        y1 = None
        x2 = None
        y2 = None
        g = 0 # start counter to read lines
        while g < 18:
            #print "Debug g =", g
            #print "Debug: Read line  g = %s Value = %s "%(str(g),str(line))
            _k = self.readLine()
            #print "Debug: Read line g = %s k =  %s "%(str(g),str(k))
            """if g == 5:# this line contains color property
            we can get the color presently not implemented
            color=(float(k[0:-1]))"""
            dPrint( "line value k="+_k)
            if _k[0:3] == ' 10':
                dPrint( "debug 10"+ _k)
                # this line of file contains start point"X" co ordinate
                #print "Debug: Convert To flot x1: %s" % str(k[0:-1])
                _k = self.readLine()
                x1 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':# this line of file contains start point "Y" co ordinate
                #print "Debug: Convert To flot y1: %s" % str(k[0:-1])
                _k = self.readLine()
                y1 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':# this line of file contains start point "Z" co ordinate
                #print "Debug: Convert To flot z1: %s" % str(k[0:-1])
                _k = self.readLine()
                z1 = (float(_k[0:-1])) 
                continue
                # Z co ordinates are not used in PythonCAD we can live without this line
            if _k[0:3] == ' 11':# this line of file contains End point "X" co ordinate
                #print "Debug: Convert To flot x2: %s" % str(k[0:-1])
                _k = self.readLine()
                x2 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 21':# this line of file contains End point "Y" co ordinate
                #print "Debug: Convert To flot y2: %s" % str(k[0:-1])
                _k = self.readLine()
                y2 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 31':# this line of file contains End point "Z" co ordinate
                #print "Debug: Convert To flot z2: %s" % str(k[0:-1])
                _k = self.readLine() 
                z2 = (float(_k[0:-1]))
            '''if _k[0:3] == ' 62':# COLOR
                _k = self.readLine() 
                c = (float(_k[0:-1]))                
                g = 30
                continue'''
                #Z co ordinates are not used in PythonCAD we can live without this line
            g+=1
        if not ( x1==None or y1 ==None or
           x2==None or y2 ==None ):
            self.createLine(x1,y1,x2,y2)
        else:
            _msg=u'Read parameter from file x1: [%s] y1: [%s] x2: [%s] y2: [%s]'%(
                        str(x1),str(y1),str(x2),str(y2))
            self.writeError('createLineFromDxf',_msg)

    def createLine(self,x1,y1,x2,y2):
        """
          Create the line into the current drawing
          In this implementation all the lines gose to the active layer and use the global settings of pythoncad
          Feauture implementation could be :
          1) Create a new layer(ex: Dxf Import)
          2) Read dxf import style propertis and set it to the line
        """    
        dPrint( "Debug Creatre line %s,%s,%s,%s"%(str(x1),str(y1),str(x2),str(y2)) )
        _active_layer = self.__dxfLayer
        _p1 = Point(x1, y1)
        _active_layer.addObject(_p1)
        _p2 = Point(x2, y2)
        _active_layer.addObject(_p2)
        _s = self.__image.getOption('LINE_STYLE')
        _seg = Segment(_p1, _p2, _s)
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
          _seg.setLinetype(_l)
        _c = '#ffff00'
        #_c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
          _seg.setColor(_c)
        print _c
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
          _seg.setThickness(_t)
        _active_layer.addObject(_seg)
    
    def createCircleFromDxf(self):
        """
            Read and create the Circle into drawing
        """
        dPrint( "Debug createCircleFromDxf" )
        g = 0 # reset g
        while g < 1:
            _k = self.readLine()
            dPrint( "line value k="+ _k)
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 40':
                _k = self.readLine()
                r = (float(_k[0:-1]))
                g = 10 # g > 1 for break
                'I need a "create Circle code" here to append the segment to image'
        self.createCircle(x,y,r)
        
    def createCircle(self,x,y,r):
        """
            create a circle entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        _center = Point(x, y)
        _active_layer.addObject(_center)
        _s = self.__image.getOption('LINE_STYLE')
        _circle = Circle(_center, r, _s)        
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
            _circle.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
            _circle.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
            _circle.setThickness(_t)
        _active_layer.addObject(_circle)
    def createTextFromDxf(self):
        """
            Read and create the Circle into drawing
        """
        dPrint( "Debug createTextFromDxf" )
        g = 0 # reset g
        x = None
        y = None
        h = None
        _t= ''
        while g < 1:
            _k = self.readLine()
            dPrint("line value k="+ _k)
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                #print "Text Loc x =", x
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                #rint "Text Loc y =", y
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
                #print "Text Loc z =", z
                continue
            if _k[0:3] == ' 40':
                _k = self.readLine()
                h = (float(_k[0:-1]))
                dPrint("Text Height =%s"%str(h))
                continue
            if _k[0:3] == '  1':
                _k = self.readLine()
                _t = _k.replace('\~', ' ')
                _t = _t.replace('\P', '\n')
                #print "Text itself is ", x, y, z, 'height', h, _t#
                g = 10 # g > 1 for break
                continue
        if not (x is None or y is None or h is None):
            self.createText(x,y,h,_t)
        else:
            _msg="Read parameter from file x: [%s] y: [%s] h: [%s] t: [%s]"%(
                        str(x),str(y),str(h),str(_t))
            self.writeError("createTextFromDxf",_msg)

    def createArcFromDxf(self):
        """
            Read and create the ARC into drawing
        """ 
        g = 0 # reset g
        while g < 1:
            _k = self.readLine()
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
            if _k[0:3] == ' 40':
                _k = self.readLine()
                r = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 50':
                _k = self.readLine()
                sa = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 51':
                _k = self.readLine()
                ea = (float(_k[0:-1]))
                g = 10 # g > 1 for break\\
                continue
        self.createArc(x,y,sa,ea,r)

    def createArc(self,x,y,sa,ea,r):
        """
            Create a Arc entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        _center = Point(x, y)
        _active_layer.addObject(_center)
        _s = self.__image.getOption('LINE_STYLE')
        py = (22.0/7.0)
        ex = x + r*math.cos((sa*py)/180)
        ey = y + r*math.sin((sa*py)/180)
        lpx = x + r*math.cos((ea*py)/180)
        lpy = y + r*math.sin((ea*py)/180)
        ep = Point(ex, ey)
        lp = Point(lpx, lpy)
        _active_layer.addObject(ep)
        _active_layer.addObject(lp)
        _arc = Arc(_center, r, sa, ea, _s)
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
            _arc.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
            _arc.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
            _arc.setThickness(_t)
        _active_layer.addObject(_arc)

    def createText(self,x,y,h,t):
        """
            Create a Text entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        try:
            _text = t.replace('\x00', '').decode('utf8', 'ignore').encode('utf8')
        except:
            self.writeError("createText","Debug Error Converting in unicode [%s]"%t)
            _text ='Unable to convert in unicode'
        _x, _y = x, y
        _ts = self.__image.getOption('TEXT_STYLE')
        _tb = TextBlock(_x, _y, _text, _ts)

        _f = self.__image.getOption('FONT_FAMILY')
        if _f != _ts.getFamily():
            _tb.setFamily(_f)

        _s = self.__image.getOption('FONT_STYLE')
        if _s != _ts.getStyle():
            _tb.setStyle(_s)

        _w = self.__image.getOption('FONT_WEIGHT')
        if _w != _ts.getWeight():
            _tb.setWeight(_w)
            
        _c = self.__image.getOption('FONT_COLOR')
        if _c != _ts.getColor():
            _tb.setColor(_c)
        _sz = h
        if abs(_sz - _ts.getSize()) > 1e-10:
            _tb.setSize(_sz)
        _a = self.__image.getOption('TEXT_ANGLE')
        if abs(_a - _ts.getAngle()) > 1e-10:
            _tb.setAngle(_a)
        _al = self.__image.getOption('TEXT_ALIGNMENT')
        if _al != _ts.getAlignment():
            _tb.setAlignment(_al)
        _active_layer.addObject(_tb)

    def createPolylineFromDxf(self):
        """
        Polyline creation read the line dxf section and create the line
        """
        dPrint("Exec createPolylineFromDxf")
        while True:
            _k = self.readLine()                  
            if _k[0:3] == ' 10':
                break
        points=[]
        p = ()
        t = 0
        while True:
            # this line of file contains start point"X" co ordinate
            # print "Debug: Convert To flot x1: %s" % str(k[0:-1])
            _k = self.readLine()
            x = (float(_k[0:-1]))
            _k = self.readLine()#pass for k[0:3] == ' 20'
            _k = self.readLine()
            y = (float(_k[0:-1]))
            p = (x,y)
            points.append(p)
            dPrint( str(points))
            _k = self.readLine()
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z1 = (float(_k[0:-1]))
                _k = self.readLine()
                continue
            if _k[0:3] != ' 10':
                break
            continue
        if len(points)>1:
            self.createPolyline(points)
        
    def createPolyline(self,points):
        """
            Crate poliline into Pythoncad
        """
        dPrint("Exec createPolyline")
        _active_layer = self.__dxfLayer
        _x = 0.0
        _y = 0.0
        _pts = []
        for _x, _y in points:
            dPrint(_x)
            dPrint(_y)
            _p = Point(_x, _y)
            _active_layer.addObject(_p)
            _pts.append(_p)
        dPrint("Exec createPolyline lenPts(%s)"%str(len(_pts)))
        _s = self.__image.getOption('LINE_STYLE')
        _pline = Polyline(_pts, _s)
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
          _pline.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
          _pline.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
          _pline.setThickness(_t)
        _active_layer.addObject(_pline)


    
def dPrint(msg):
    """
        Debug function for the dxf file
    """
    if dxfDebug :
        print "Debug: %s " %str(msg)
