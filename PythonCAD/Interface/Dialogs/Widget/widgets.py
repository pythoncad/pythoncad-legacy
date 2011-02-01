from PyQt4 import QtCore, QtGui

class BaseContainer(QtGui.QHBoxLayout):
    def __init__(self, parent=None, label="baseInfo"):
        super(BaseContainer, self).__init__(parent)
        label=QtGui.QLabel(label)
        self.addWidget(label)

        
class PyCadQColor(BaseContainer):
    def __init__(self, parent=None, oldValue='green', label="Color"):
        super(PyCadQColor, self).__init__(parent)
        r, g, b=oldValue
        self.activeColor=QtGui.QColor.fromRgb(r, g, b)
        self.pushButton=QtGui.QPushButton()
        self.pushButton.clicked.connect(self.click)
        
        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        self.colorLabel = QtGui.QLabel()
        self.colorLabel.setFrameStyle(frameStyle)
        self.addWidget(self.colorLabel)
        self.addWidget(self.pushButton)
        
    def click(self):
        color = QtGui.QColorDialog.getColor(self.activeColor)
        if color.isValid(): 
            self.colorLabel.setText(color.name())
            self.colorLabel.setPalette(QtGui.QPalette(color))
            self.colorLabel.setAutoFillBackground(True)
            self.activeColor=color
    @property
    def color(self):
        return self.activeColor
        
class PyCadQLineType(BaseContainer ):
    def __init__(self, parent=None, oldValue='dot', label="Line Type"):
        super(PyCadQLineType, self).__init__(parent)
    
class PyCadQDouble(BaseContainer ):
    def __init__(self, parent=None, oldValue='0.0', label="Double"):
        super(PyCadQDouble, self).__init__(parent)
    
class PyCadQFont(BaseContainer ):
    def __init__(self, parent=None, oldValue='green', label="Font"):
        super(PyCadQFont, self).__init__(parent)
    
    
