# Import All Modules
from configparser import ConfigParser
import os
from PyQt5.QtGui import QColor, QFont, QKeySequence, QPen, QPixmap, QPolygonF, QTransform
from GalleryMan.utils.helpers import ResizableRubberBand
from GalleryMan.assets.QtHelpers import Animation, QCustomButton
from PIL import Image
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView, QLabel, QMainWindow, QShortcut, QVBoxLayout, QWidget
from PyQt5.QtCore import QAbstractAnimation, QParallelAnimationGroup, QPoint, QPointF, QRect, QTimer, QVariant, QVariantAnimation, Qt, pyqtSignal, pyqtSlot


class QRotateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(QRotateLabel, self).__init__(*args, **kwargs)
        self._pixmap = QPixmap()

        self.curr = 0

        self.initial = 0

        self.init_ani()
        
        self.setScaledContents(True)

    def init_ani(self):
        self._animation = QVariantAnimation(
            self,
            startValue=self.initial,
            endValue=self.curr,
            duration=100,
            valueChanged=self.on_valueChanged,
        )

        self.initial = self.curr

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)

    def start_animation(self, deg):
        if self._animation.state() != QAbstractAnimation.Running:
            self.curr, self.initial = deg, self.curr

            self.init_ani()

            self._animation.start()

    def get_curr_deg(self):
        return self.curr % 360

    @pyqtSlot(QVariant)
    def on_valueChanged(self, value):
        t = QTransform()
        t.rotate(value)
        self.setPixmap(self._pixmap.transformed(t))


# Main Cropper Class
class ImageCropper(QGraphicsView):
    # Signals
    closed = pyqtSignal()

    # call the __init__ function of the QGraphicsView Class
    def __init__(self, mainWindow: QMainWindow, outWidget: QRotateLabel , config: ConfigParser):
        super().__init__(mainWindow)
        
        # Get the original responser so that it could be replaced on removing
        self.originalResponser = mainWindow.resizeEvent
        
        # Create a scene which will contain all the images and rest
        self.setGeometry(mainWindow.geometry())
        
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.myScene = QGraphicsScene()
        
        self.myScene.addPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
        
        self.setScene(self.myScene)
        
        self.verticalScrollBar().setValue(0) 
        
        self.horizontalScrollBar().setValue(0)
        
        # Create a resizable label for cropping
        self.cropper = ResizableRubberBand()
    
        # Add to scene
        self.scene().addWidget(self.cropper)
        
        # Set geometry
        self.cropper.setGeometry(QRect(280, 120, 300, 300))
        
        # Show the cropper
        self.cropper.show()
        

        self.outWidget = outWidget

        self.shortcut = QShortcut(QKeySequence("Ctrl+S") , self)
        
        self.shortcut.activated.connect(self.continueCropping)
        
        self.starter()
    
    def showToolTip(self):
        
        # A Custom, Beautiful Tooltip is getting drawn!
        polygon = QPolygonF()
        
        pen = QPen()
        
        # Set color of the pen (border)
        pen.setColor(QColor("#2E3440"))
        
        
        # Iterate over the points that will be used for deviation
        for points in [QPoint(100 , 100 - 50) , QPoint(500 , 100 - 50) , QPoint(500 , 160 - 50 - 10) , QPoint(300 , 160 - 50 - 10) , QPoint(290 , 170 - 50 - 10) , QPoint(280 , 160 - 50 - 10) , QPoint(280 , 160 - 50 - 10) , QPoint(100 , 160 - 50 - 10) , QPoint(100 , 100 - 50 + 10)]:
            polygon.append(QPointF(points))
            
        # Add tooltip
        self.tooltip = self.scene().addPolygon(polygon , pen)
        
        # Fill
        self.tooltip.setBrush(QColor("#2E3440"))
        
        # Set custom font and pen of the text inside
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setWidth(-1)
        
        font = QFont("Comfortaa" , 15)
        
        text = QGraphicsSimpleTextItem("Drag these to increase the size" , self.tooltip)
        
        text.setBrush(QColor("#88C0D0"))
        
        text.setPen(pen)
        
        text.setFont(font)
        
        # Align 
        rect = text.boundingRect()
        
        bounding = self.tooltip.boundingRect()
            
        rect.moveCenter(QPointF(bounding.center().x() , bounding.center().y() - 5))
        
        text.setPos(rect.topLeft())      
        
          
        # Show the tooltip with an animation
        self.animation = QParallelAnimationGroup()
        
        self.animation.addAnimation(Animation.fadingAnimation(Animation , self.tooltip , 200 , True))   
        
        self.animation.start()

    
    def continueCropping(self):
        """Saves the cropped image"""
        
        #  A function which will do additional changes when the animation is over
        def next():
            
            # Hide the graphics
            self.hide()

            # Set the updated image as the preview
            self.outWidget.set_pixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
        
        # Open the image using PIL
        image = Image.open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        # Get cropping coordinates
        x, y, width, height = (
            self.cropper.geometry().x(),
            self.cropper.geometry().y(),
            self.cropper.geometry().width(),
            self.cropper.geometry().height(),
        )
        
        # Crop
        image = image.crop((x, y, width + x, height + y))
        
        # Save
        image.save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        # Animation
        self.animation = Animation.fadingAnimation(Animation , self , 300)
        
        self.animation.finished.connect(next)
        
        self.animation.start()
        
        self.shortcut.setKey(QKeySequence())
            
    def hideHelp(self):
        self.animation = Animation.fadingAnimation(Animation , self.tooltip , 200)
        
        self.animation.start()
        
    def starter(self):
        def run_second():
            self.animation = Animation.fadingAnimation(Animation , self.helpLabel , 200)
            
            self.animation.start()
            
            self.animation.finished.connect(self.helpLabel.hide)
            
            self.animation.finished.connect(self.showToolTip)

            self.timer = QTimer(self)
            
            self.timer.setSingleShot(True)
            
            self.timer.timeout.connect(self.hideHelp)
            
            self.timer.start(2000)
        
        self.helpLabel = QWidget(self)
        
        self.helpLabel.setGeometry(self.geometry())
        
        helpLayout = QVBoxLayout()
        
        text = QLabel(text="Press Ctrl+S to save and exit")
        
        helpLayout.addWidget(text , alignment=Qt.AlignBottom | Qt.AlignCenter)
        
        text.setStyleSheet("background-color: transparent; font-size: 30px")
        
        helpLayout.setSpacing(40)
        
        button = QCustomButton("Okay!" , None).create()
        
        button.setFixedHeight(100)
        
        button.clicked.connect(run_second)
        
        button.setFixedWidth(600)
        
        button.setStyleSheet("background-color: transparent; border: 1px solid #2E3440; font-size: 30px")
        
        helpLayout.addWidget(button , alignment=Qt.AlignTop | Qt.AlignCenter)
        
        self.helpLabel.setLayout(helpLayout)
        
        self.helpLabel.setStyleSheet("""background-color: rgba(46, 52, 64, 155)""")
        
        self.animation = Animation.fadingAnimation(Animation , self.helpLabel , 200 , True)
        
        self.animation.start()
        
        self.animation.finished.connect(self.helpLabel.show)
        