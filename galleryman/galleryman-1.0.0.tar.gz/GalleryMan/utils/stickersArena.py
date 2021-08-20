from PIL import Image
from PyQt5.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QImage, QKeySequence, QMouseEvent, QPainter, QPixmap, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QShortcut, QSizePolicy, QVBoxLayout, QWidget
import functools
import os
from GalleryMan.assets.QtHelpers import Animation, QCustomButton, QSliderMenu
from GalleryMan.utils.doodleImage import ClickableLabel

class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None, listenFor=Qt.LeftButton):
        super().__init__(parent=parent)

        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == self.listenFor:
            self.clicked.emit(event.pos())

            self.eventPos = event.pos()


class stickersViewer:
    STOCK_PATH = os.path.join(os.path.expanduser("~") , ".galleryman" , "stickers")
    
    def __init__(self , parent , renderArea , scrollArea: QScrollArea , callback):
        self.inGraphics = False
        
        self.callback = callback
        
        # Make args global
        self.parent = parent 
        
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        self.original = scrollArea.widget()
        
        self.originalGeo = scrollArea.widget().geometry()
        
        self.grandparentsLayout = QHBoxLayout()
        
        
        # QGraphics and QScene
        self.graphics = QGraphicsView(self.parent)

        self.graphics.move(QPoint(0 , 0))
        
        self.graphics.setFixedSize(parent.size())
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scene = QGraphicsScene()
        
        self.graphics.setScene(self.scene)
        
        self.pixmap = self.scene.addPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
                
        # Scroll Widget
        self.widget = QWidget()
        
        # Take the old widget
        self.oldWidget = self.scrollArea.takeWidget()
        
        # Set new sizes 
        self.widget.setFixedHeight(100)
        
        self.widget.setFixedWidth(3000)
        
        # Stylings
        self.widget.setStyleSheet(self.oldWidget.styleSheet())
        
        self.stickersDict: list[QVBoxLayout] = {}
        
        self.shortcut = QShortcut(QKeySequence("Ctrl+S") , self.graphics)
        
        self.shortcut.activated.connect(self.attachSticker)
        
        # Parent layout to store both the name and the stickers preview
        self.parentlayout = QVBoxLayout()
        
        self.grandparentsLayout.addLayout(self.parentlayout)
        
        self.nameLayout = QHBoxLayout()
        
        self.parentlayout.addLayout(self.nameLayout)
        
        self.cross = ClickableLabel("" , None)
        
        self.cross.setBaseSize(50 , 50)
        
        self.cross.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.cross.clicked.connect(self._callback)
        
        self.grandparentsLayout.addWidget(self.cross)
        
        self.widget.setLayout(self.grandparentsLayout)
        
        self.scrollArea.setWidget(self.widget)
        
        print(scrollArea.widget().size())
        
        
        
    def initStock(self):
        directories = os.listdir(self.STOCK_PATH)
        
        # Iterate through all the folders in the folders path
        for dirs in directories:
            
            self.preview = QHBoxLayout()
            
            # Get the parent
            parent = os.path.join(self.STOCK_PATH , dirs)
                        
            # Check if it is a directory
            if(not os.path.isdir(parent)): continue
            
            # Add a label to the name's layout
            name = QCustomButton(dirs , None).create()
                        
            name.setStyleSheet("""
                font-size: Comfortaa;
                font-size: 20px;                   
            """)
            
            name.clicked.connect(functools.partial(self.switchTo , parent))
            
            self.nameLayout.addWidget(name)
            
            sticker = os.listdir(parent)
            
            self.widget.setFixedWidth(len(sticker) * 100)
            
        self.switchTo(parent)
                        
    def useSticker(self , name , event):
        self.inGraphics = True
        
        self.scene.clear()
        
        self.pixmap = self.scene.addPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
        
        self.graphics.show()
        
        self.currentlyUsing = name
        
        self.sticker = self.scene.addPixmap(QPixmap(name))
    
        self.sticker.setPos(QPoint(75 , 75))    
        
        self.sticker.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.menu = QSliderMenu(self.graphics)
        
        crossLabel = QVBoxLayout()
        
        cross = QLabel()
        
        cross.setFixedSize(QSize(50 , 50))
        
        cross.setText("")
        
        self.config = {
            "Width": 300,
            "Height":300,
            "Rotation": 0
        }
        
        crossLabel.addWidget(cross , alignment=Qt.AlignTop | Qt.AlignLeft)
        
        self.menu.addMenu("" , crossLabel , True)
        
        for name in ["Width" , "Height" , "Rotation"]:
            inputBox = QLineEdit()
            
            inputBox.setPlaceholderText(name)
            
            inputBox.setStyleSheet("""
                color: #D8DEE9;
                padding-left: 20px;    
            """)
            
            inputBox.setFixedHeight(50)
            
            inputBox.textChanged.connect(functools.partial(self.update , inputBox , name))
            
            self.menu.addMenu(name , inputBox)
            
        self.menu.move(QPoint(self.graphics.width() + 200 , 0))
        
        self.menu.show()
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1877 - self.menu.width(), 0) , 200)
                
        self.animation.start()
        
        
    def update(self , inputBox , name):
        text = int(inputBox.text())
        
        self.config[name] = text
        
        self.scene.removeItem(self.sticker)
        
        self.sticker.hide()
        
        pos = self.sticker.pos()
        
        self.sticker = self.scene.addPixmap(QPixmap(self.currentlyUsing).scaled(self.config["Width"] , self.config["Height"] , transformMode=Qt.SmoothTransformation))
        
        self.sticker.setPos(pos)
        
        self.sticker.setFlag(QGraphicsItem.ItemIsMovable)
        
        self.sticker.show()
                
        self.sticker.setTransformOriginPoint(self.sticker.boundingRect().center())
        
        self.sticker.setTransform(QTransform().rotate(self.config["Rotation"]))
        
    def switchTo(self , name):
        def run_second():     
            # Get the old widget
            oldWidget = self.scrollArea.takeWidget()
            
            # Create a new widget
            parent = QWidget()
            
            parent.setStyleSheet(oldWidget.styleSheet())
            
            parent.setGeometry(oldWidget.geometry())
            
            self.preview = QHBoxLayout()
            
            # Create a grand parent layout
            grandLayout = QHBoxLayout()
                                    
            # Add cross button to it
            self.cross.setParent(None)
            
            # Set Fixed Size and Policy
            self.cross.setFixedSize(50 , 50)
            
            self.cross.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            
            # grandLayout.addWidget(self.cross)
            
            layout = QVBoxLayout()
            
            
            self.nameLayout.setParent(None)
            
            layout.addLayout(self.nameLayout)
                        
            # Iterate through all the stickers in the folder
            for stickers in os.listdir(name):
                
                # Create a clickable label
                preview = CustomLabel()
                
                
                # Set fixed size
                preview.setFixedSize(50 , 50)
                
                # Scaled contents
                preview.setScaledContents(True)
                
                # Set the image
                preview.setPixmap(QPixmap(os.path.join(name , stickers)).scaled(50 , 50 , transformMode=Qt.SmoothTransformation))
                
                # Call the function which will handle the usage of the sticker on click
                preview.clicked.connect(functools.partial(self.useSticker , os.path.join(name , stickers)))
                
                # Set the cursor
                preview.setCursor(QCursor(Qt.PointingHandCursor))
                
                # Add the widget to the preview
                self.preview.addWidget(preview)
                
            self.preview.addWidget(self.cross)
            
            self.preview.setParent(None)
                
            layout.addLayout(self.preview)
                                    
            parent.setFixedWidth(self.preview.count() * 130)
                                        
            grandLayout.addLayout(layout)
            
            layout.setParent(None)
                
            parent.setLayout(layout)
        
            self.scrollArea.setWidget(parent)
            
            self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200 , True)
            
            self.animation.start()
            
        self.animation = Animation.fadingAnimation(Animation , self.scrollArea.parent() , 200)
        
        self.animation.finished.connect(run_second)
        
        self.animation.start()
        
    def attachSticker(self):        
        if(not self.inGraphics):
            return
        
        
        # Callback
        def callback():
            self.graphics.hide()
            
            self.renderArea.set_pixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
            
            self.graphics = QGraphicsView(self.parent)

            self.graphics.move(QPoint(0 , 0))
            
            self.graphics.setFixedSize(self.parent.size())
            
            self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            self.scene = QGraphicsScene()
            
            self.graphics.setScene(self.scene)
            
            self.pixmap = self.scene.addPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
            
            self.shortcut.setParent(self.graphics)
            
        
        self.menu.hide()
        
        # Open the image
        self.image = Image.open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        # Get the geometry
        area = QRect(0 , 0 , self.image.width , self.image.height)
        
        # Parse the image 
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        
        painter = QPainter(image)
        
        self.scene.render(painter, QRectF(image.rect()), QRectF(area))
        
        painter.end()
        
        # Save the new image
        image.save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        # Hide the graphics
        self.animation = Animation.fadingAnimation(Animation , self.graphics , 200)
        
        self.animation.finished.connect(callback)
        
        self.animation.start()
        
        self.inGraphics = False

        
    def _callback(self):
        self.scrollArea.widget().setGeometry(self.originalGeo)
        
        
        print(self.originalGeo)
        
        self.callback(self.originalGeo)