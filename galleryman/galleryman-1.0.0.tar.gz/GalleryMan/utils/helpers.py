# Importing the modules
import os
from GalleryMan.utils.initer import bcolors
from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPainter 

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRubberBand,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)
from json import loads, dumps

# A Custom, Draggable label
class DraggableLabel(QLabel):
    moved = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("background: transparent;")

        self.origin = None

    def setLimits(self, rect):
        self.limits = rect
        
    # Listen for mouse events
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

            self.moved.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

            self.moved.emit()

# A Draggable input
class DraggableInput(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background: transparent;")
        self.origin = None

    def setLimits(self, rect):
        self.limits = rect

    # Mouse listens
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                if not self.limits.contains(self.geometry()):
                    self.move(self.origin)
        except:
            pass


# Class for ading to like
class AddToLiked:
    def __init__(self, parent, dir, remove=False):
        self.dir = dir

        self.remove = remove

    def run(self):
        with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "likedFolders.txt"), "r") as f:
            data = f.read()
  
            data = loads(data)

        with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "likedFolders.txt"), "w") as f:
            if self.remove and self.dir in data:
                data.remove(self.dir)

            else:
                data.append(self.dir)

            f.write(dumps(data))


class ResizableRubberBand(QWidget):
    def __init__(self, parent=None):
        
        super(ResizableRubberBand, self).__init__(parent)
            
        self.mousePressPos = None
        
        self.timer = QTimer(self)
        
        self.timer.setSingleShot(True)
        
        
        
        self.needHelp = True
        
        self.mouseMovePos = None
        
        self.origin = None
        
        self.borderRadius = 0

        self.setWindowFlags(Qt.SubWindow)
        
        layout = QHBoxLayout(self)
        
        layout.setContentsMargins(0, 0, 0, 0)
        
        grip1 , grip2 = QSizeGrip(self) , QSizeGrip(self)
        
        grip1.setStyleSheet("""background-color: #FFFFFF""")
            
        grip2.setStyleSheet("""background-color: #FFFFFF""")

            
        layout.addWidget(
            grip1, 0,
            Qt.AlignLeft | Qt.AlignTop)
        
        layout.addWidget(
            grip2, 0,
            Qt.AlignRight | Qt.AlignBottom)
        
        self._band = QRubberBand(
            QRubberBand.Rectangle, self)
        
        self.setStyleSheet("""
            background-color: #2E344050;
        """)
                        
        self._band.show()
        
    def resizeEvent(self, event):
        self._band.resize(self.size())

    def paintEvent(self, event):
        window_size = self.size()
            
        qp = QPainter()

        qp.begin(self)

        qp.setRenderHint(QPainter.Antialiasing, True)

        qp.drawRoundedRect(0, 0, window_size.width(), window_size.height(),
                           self.borderRadius, self.borderRadius)
        
        qp.end()
        
        
    def mousePressEvent(self, event):
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        pos = self.pos() + event.pos() - self.mousePos
        if event.buttons() == Qt.LeftButton:
            self.move(pos)
            

    def mouseReleaseEvent(self, event):
        pos = self.pos() + event.pos() - self.mousePos
        if event.button() == Qt.LeftButton:
            self.move(pos)
    
            
class QGripLabel(QLabel):
    def __init__(self , parent=None , movable=True):
        super().__init__(parent)
        
        self.addGrips()
        
        self.origin = None
        
        self.movable = movable
        
        self.mousePos = None
        
    def addGrips(self):
        self.setWindowFlags(Qt.SubWindow)
        
        self.grip1 , self.grip2 = QSizeGrip(self) , QSizeGrip(self)
        
        layout = QVBoxLayout()
        
        layout.setContentsMargins(0 , 0 , 0 , 0)
        
        layout.addWidget(self.grip1 , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(self.grip2 , alignment=Qt.AlignBottom | Qt.AlignRight)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if(not self.movable): return
        
        if not self.origin:
            self.origin = self.pos()
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if(not self.movable): return
        
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)

    def mouseReleaseEvent(self, event):
        if(not self.movable): return
        
        if event.button() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.mousePos)
            
            
def show_list():
    print(bcolors.HEADER , "\b\nList of Directories Prevented To Be Scanned: \n" , bcolors.ENDC)
    
    with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "scan_dirs.txt")) as f:
        data = loads(f.read())
        
        for index , directory in enumerate(data):
            print("{}: {}".format(bcolors.OKCYAN + str(index) , bcolors.OKGREEN + directory))

def addToScanDirectory(self):
    print(bcolors.OKGREEN + "Enter the folder path (Press enter to select current directory): ", end="")
    
    directory = input()
    
    if(directory in ["." , ""]):
        directory = os.getcwd()
        
    elif(directory == "~"):
        directory= os.path.expanduser("~")
        
    print(bcolors.WARNING + "\nAdding {} to scanning list".format(directory))
    
    with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "scan_dirs.txt")) as f:
        curr = loads(f.read())
        
    curr.append(directory)
    
    print(bcolors.OKGREEN + "\nSuccessfully added to scanning list.")
    
def removeFromScanDirectory(directory):
    print(bcolors.OKGREEN + "Enter the folder path (Press enter to select current directory): ", end="")
    
    directory = input()
    
    if(directory in ["." , ""]):
        directory = os.getcwd()
        
    elif(directory == "~"):
        directory= os.path.expanduser("~")
        
    print(bcolors.WARNING + "\nRemoving {} from scanning list".format(directory))
    
    with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "scan_dirs.txt")) as f:
        curr = loads(f.read())
        
    try:
        curr.remove(directory)
        
        print(bcolors.OKGREEN + "\nSuccessfully added to scanning list.")
    except:
        print(bcolors.FAIL + "\nCannot remove directory from the scanning list. Aborting...")
        
        print(bcolors.FAIL + "HELP: Directory not in scanning list")
        
        
    
class LongProcessor(QObject):
    finished = pyqtSignal()
    ready = pyqtSignal()
    
    def run(self):
        self.ready.emit()