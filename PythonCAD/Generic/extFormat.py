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

import os.path

class ExtFormat:
    """
        This class provide base class for hendly different drawing format in pythoncad
    """
    def __init__(self,gtkImage):
        """
            Default Constructor
        """
        self.__Tool=gtkImage.getTool()
        self.__GtkImage=gtkImage
    def openFile(self,fileName):
        """
           Open a generic file 
        """
        path,exte=os.path.splitext( fileName )
        if( exte.upper()==".dxf".upper()):
            dxf=Dxf(gtkImage,fileName)

class DrawingFile:
    """
        This Class provide base capability to read write a  file
    """
    def __init__(self,fileName):
        """
            Base Constructor
        """
        self.__fn=fileName
        self.__fb=None
    def ReadAsci(self):
        """
            Read a generic file 
        """
        self.__fb=open(self.__fn,'r')
    def FileObject(self):
        """
            Return the file opened 
        """
        if(self.__fb!=None): return self.__fb
        else: return None

class Dxf(DrawingFile):
    """
        this class provide dxf reading/writing capability 
    """
    def __init__(self,gtkImage):
        """
            Default Constructor
        """
        self.__gtkI=gtkImage
    def OpenFile(fileName):
        """
            Open The file and create The entity in pythonCad
        """
        self.ReadAsci();
        fo=self.FileObject()
        if(fo!=None):
            "Implement here your methon"
    
