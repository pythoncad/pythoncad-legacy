##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 24/apr/2012 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    info@omniasolutions.eu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
Created on 24/apr/2012

@author: mboscolo
'''


from PyQt4.QtGui    import QDialog,QAbstractItemView
from PyQt4.QtCore   import pyqtSignature

from Ui_preferences    import Ui_preferences

from Interface.cadinitsetting import *

class Preferences(QDialog, Ui_preferences):
    """
        this class define the entity property dialog
        it automaticaly retrive the style property 
        and show it in the form
    """
    def __init__(self, parent = None, entity=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
 
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
            implements the accept button
        """
        self.close()
        
    @pyqtSignature("")
    def on_buttonBox_rejected(self):
        """
            implements the accept button
        """
        self.close()



