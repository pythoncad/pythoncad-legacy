from PyQt4 import QtCore, QtGui

class BaseContainer(QtGui.QHBoxLayout):
    def __init__(self, parent=None, label="baseInfo"):
        super(BaseContainer, self).__init__(parent)
        label=QtGui.QLabel(label)
        self.addWidget(label)
        self.activeValue=None
        self._changed=False
    @property
    def value(self):
        """
            return the value of the object
        """
        return self.activeValue
    @property
    def changed(self):
        """
            tells if the value is changed
        """
        return self._changed
    @changed.setter  
    def changed(self, value):
        """
            tells if the value is changed
        """
        self._changed=value
        
class PyCadQColor(BaseContainer):
    def __init__(self, parent=None, oldValue='green', label="Color"):
        super(PyCadQColor, self).__init__(parent=parent, label=label)
        r, g, b=oldValue
        self.activeValue=oldValue
        self.pushButton=QtGui.QPushButton()
        self.pushButton.clicked.connect(self.click)
        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        self.colorLabel = QtGui.QLabel()
        self.colorLabel.setFrameStyle(frameStyle)
        sColor=QtGui.QColor.fromRgb(r, g, b)
        self.colorLabel.setText(sColor.name())
        self.colorLabel.setPalette(QtGui.QPalette(sColor))
        self.colorLabel.setAutoFillBackground(True)
        self.addWidget(self.colorLabel)
        self.addWidget(self.pushButton)
        
    def click(self):
        r, g, b=self.activeValue
        sColor=QtGui.QColor.fromRgb(r, g, b)
        color = QtGui.QColorDialog.getColor(sColor, parent=None)
        if color.isValid(): 
            self.colorLabel.setText(color.name())
            self.colorLabel.setPalette(QtGui.QPalette(color))
            self.colorLabel.setAutoFillBackground(True)
            self.activeValue=(color.red(), 
                              color.green(), 
                              color.blue()
                              )
            self.changed=True
            

        
class PyCadQLineType(BaseContainer ):
    def __init__(self, parent=None, oldValue='dot', label="Line Type"):
        super(PyCadQLineType, self).__init__(parent, label)
    
class PyCadQDouble(BaseContainer ):
    def __init__(self, parent=None, oldValue='0.0', label="Double"):
        super(PyCadQDouble, self).__init__(parent, label)
    
class PyCadQFont(BaseContainer ):
    def __init__(self, parent=None, oldValue='green', label="Font"):
        super(PyCadQFont, self).__init__(parent, label)
    
    
