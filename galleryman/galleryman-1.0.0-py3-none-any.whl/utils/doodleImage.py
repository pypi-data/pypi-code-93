from GalleryMan.assets.QtHelpers import Animation, QSliderMenu
from functools import partial
import os
from PIL import Image , ImageDraw
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QPointF, QPropertyAnimation, QRect, QRectF, QTimer, Qt, pyqtBoundSignal, pyqtSignal 
from PyQt5.QtGui import QColor, QFont, QImage, QKeySequence, QMouseEvent, QPainter, QPen, QPixmap, QPolygonF
from PyQt5.QtWidgets import QCheckBox, QGraphicsLineItem, QGraphicsOpacityEffect, QGraphicsSimpleTextItem, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QShortcut, QVBoxLayout, QWidget
from GalleryMan.assets.cropper import QRotateLabel

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self , *arg , **kwargs):
        super().__init__(*arg , **kwargs)
        
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clicked.emit()
        
        try:        
            return QLabel.mousePressEvent(self , a0)
        except:
            return None
    

class customLineItem(QGraphicsLineItem):
    changeStyles = pyqtBoundSignal(QGraphicsLineItem)
    
    def __init__(self , x1 , y1 , x2 , y2 , pen , callback):
        super().__init__(x1 , y1 , x2 , y2)
        
        self.setPen(pen)
        
        self.enableMouseTracking = False
        
        self.callback = callback

class doodleShape:
    drawingCompleted = pyqtSignal(list)
    
    def __init__(self , parent: QGraphicsView , renderArea: QRotateLabel , dir: str):
        self.parent = parent
        
        self.renderArea = renderArea
        
        self.areTheyShown = False
            
        self.config = {
            "width": 5,
            "color": "#88C0D0",
        }
        
        self.shortcut = QShortcut(QKeySequence("Ctrl+X") , self.parent)
        
        self.shortcut.activated.connect(self._breakSupport)
        
        self.parent.setMouseTracking(True)
        
        self.parent.mousePressEvent = lambda event: self.onClick(event)
        
        self.parent.mouseMoveEvent = self.increase
        
        self.undoShortcurt = QShortcut(QKeySequence("Ctrl+Z") , parent)
        
        self.undoShortcurt.activated.connect(self.undoHandler)
        
        self.pointsLocation: list[QPoint] = []
        
        self.lineInited = False
        
        self.isHandleAvail = False
        
        self.breakSupport = False

        self.image = Image.open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")).convert("RGBA")
        
        self.draw = ImageDraw.ImageDraw(self.image)
        
        self.menu = QSliderMenu(self.parent)
        
        self.label = QLabel("Right click to connect to the starting point" , self.parent)
        
        self.label.setStyleSheet("font-size: 20px; color: white; background-color: transparent ")
        
        self.label.hide()
        
        self.lineLayersParent = QLabel(self.parent)
        
        layout = QVBoxLayout()
        
        self.lineLayers = QWidget()
        
        self.lineLayers.setProperty("class" , "need")
        
        self.lineLayers.setFixedHeight(50)
        
        self.lineLayers.setStyleSheet("background-color: rgba(46, 52, 64, 200)")
        
        self.lineLayersParent.setGeometry(QRect(0 , 0 , self.parent.width() , 70))
        
        self.lineLayersParent.setLayout(layout)
        
        self.lineLayersParent.show()
        
        self.lineLayersParent.setStyleSheet("background-color: transparent")
        
        self.scrollArea = QScrollArea()
        
        self.scrollArea.setGeometry(self.lineLayersParent.geometry())
        
        self.scrollArea.setFixedWidth(self.parent.width() - 500)
        
        self.scrollArea.setStyleSheet("background-color: transparent")
        
        self.scrollArea.setFixedHeight(100)
        
        self.scrollArea.widget()
        
        self.scrollArea.setWidget(self.lineLayers)
        
        layout.addWidget(self.scrollArea)
        
        self.width = self.height = 0 
        
        self.count = 1
        
        self.layerLayout = QHBoxLayout()
        
        self.lineLayers.setLayout(self.layerLayout)

        self.lines: list[QGraphicsLineItem] = []
        
        self.poped = []
        
        self.label.setGeometry(QRect(0 , 0 , 1000 , 50))
        
        self.showHelp()
        
        self.lineLayersParent.hide()
        
        self.dir = dir
        
    def _breakSupport(self):
        self.breakSupport = True
        
        try:
            self.lines.pop(self.line)
            
        except:
            pass
        
        self.button.setParent(None)
        
        self.shortcut.setKey(QKeySequence())
        
        self.line.hide()
        
        self.lineLayers.setProperty("class" , "need")
        
        self.lineLayers.setStyleSheet(""" QWidget[class="need"]{ background-color: #2E3440; border: 2px solid #3B4252 }""")
        
        self.lineLayersParent.move(QPoint(
            0 , self.parent.height() - self.lineLayersParent.height() - 72
        ))
        
        self.lineLayersParent.show()
        
        self.showToolTip()
        
        self.timer = QTimer(self.parent)
        
        self.timer.setSingleShot(True)
        
        self.animation = Animation.fadingAnimation(Animation , self.tooltip , 300)
        
        self.timer.timeout.connect(self.animation.start)
        
        self.timer.start(1000)
        
        self.animation.finished.connect(self.tooltip.hide)

    def initPointLine(self , position: QPoint , followMouse=False):
        if(self.breakSupport): return
                
        position.setX(position.x() + self.parent.horizontalScrollBar().value())
        
        position.setY(position.y() + self.parent.verticalScrollBar().value())
        
        scene = self.parent.scene()
                
        self.pen = QPen()
        
        self.pen.setColor(QColor(self.config["color"]))
        
        self.pen.setJoinStyle(Qt.RoundJoin)
        
        self.pen.setWidth(int(self.config["width"]))
        
        self.pointsLocation.append(position.__pos__())
        
        self.lineInited = True

        self.line = customLineItem(position.x() , position.y() , position.x() + 0.5 , position.y() + 0.5, self.pen , self.updateSingleLine)
        
        scene.addItem(self.line)
        
        self.lines.append(self.line)
        
        self.button = ClickableLabel(str(self.count) , None)
        
        self.button.setCursor(Qt.PointingHandCursor)
            
        self.button.setFixedSize(30 , 30)
        
        self.button.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)
        
        self.button.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        self.button.clicked.connect(partial(self.updateSingleLine , self.line))
        
        self.width += len(str(self.count)) * 30
        
        self.lineLayers.setFixedWidth(self.width)
        
        self.layerLayout.addWidget(self.button , alignment=Qt.AlignCenter | Qt.AlignCenter)
        
        self.count += 1
                    
    def increase(self , event: QMouseEvent):
        if(not self.lineInited or self.breakSupport): return
            
        x = event.x() + self.parent.horizontalScrollBar().value()
        
        y = event.y() + self.parent.verticalScrollBar().value()
        
        self.line.setLine(self.line.line().x1() , self.line.line().y1() , x , y)
                
        firstPointLocation = self.pointsLocation[0]
                             
        if(abs(x - firstPointLocation.x()) <= 10 or abs(y - firstPointLocation.y()) <= 10):            
            self.label.move(x , y)            
        else:
            self.isHandleAvail = False
            
            self.label.hide()
        
    def updateSingleLine(self , line: QGraphicsLineItem):
        def run_second():
            
            self.menu.hide()
        
            self.menu = QSliderMenu(self.parent)
            
            self.manageMenu()
            
        self.animation = QParallelAnimationGroup()
        
        if(self.areTheyShown == False):
            for line in self.lines:
                self.animation.addAnimation(Animation.fadingAnimation(Animation , line , 200 , endValue=0.4))

                            
            self.areTheyShown = True
                
        self.animation.addAnimation(Animation.fadingAnimation(Animation , self.line , 200 , endValue=0.4))
        
        self.animation.addAnimation(Animation.fadingAnimation(Animation , line , 200 , True , 0.4))
        
        self.animation.finished.connect(run_second)
        
        self.animation.start()

        
        self.line = line        
            
                
    def manageMenu(self):
        stylesheet = """
            border: 1px solid #4C566A;
            padding: 10px;
            padding-left: 10px;
            color: white;
        """
        
        for name in ["Width" , "Color"]:
            layout = QVBoxLayout()
            
            layout.setSpacing(20)
            
            inputBox = QLineEdit()
            
            inputBox.setPlaceholderText(name)
            
            inputBox.setFixedHeight(50)
            
            inputBox.setStyleSheet(stylesheet)
            
            inputBox.textChanged.connect(partial(self.update , name.lower().replace(' ' , '-') , inputBox))
            
            layout.addWidget(inputBox)
            
            checkbox = QCheckBox(text="Apply this {} to all the lines".format(name.lower()))
            
            checkbox.clicked.connect(partial(self.applyAll , name))
            
            checkbox.setStyleSheet("color: #D8DEE9")
            
            layout.addWidget(checkbox)
            
            self.menu.addMenu(name , layout , True)
        
        layout = QVBoxLayout()
        
        checkBox = QCheckBox(text="Straight line")
        
        checkBox.setBaseSize(50 , 50)
        
        checkBox.setStyleSheet("""
            color: #D8DEE9;
            font-family: SauceCodePro Nerd Font;
            font-size: 20px                       
        """)
                
        checkBox.clicked.connect(self.makeItStraight)
        
        layout.addWidget(checkBox)
        
        checkBox = QCheckBox(text="Remove partial hide effect")
        
        checkBox.setBaseSize(50 , 50)
        
        checkBox.setStyleSheet("""
            color: #D8DEE9;
            font-family: SauceCodePro Nerd Font;
            font-size: 20px                       
        """)
                
        checkBox.clicked.connect(self.removePartial)
        
        layout.addWidget(checkBox)
        
        self.menu.addMenu("Other options" , layout , True)   
            
        self.menu.move(QPoint(self.parent.width() + 200 , 0))
        
        self.menu.show()
        
        self.animation = Animation.movingAnimation(Animation , self.menu , QPoint(1877 - self.menu.width(), 0) , 200)
        
        self.animation.start()
    
    def makeItStraight(self):
        # Get the index
        pos = self.lines.index(self.line)
        
        # A variable to check if it is needed to change next one too
        changeNextOne = True
        
        # Check if the line is not the last line
        if(pos == len(self.lines)):
            
            # Dont change the next Line if it is the last line
            changeNextOne = False
        
        line = self.line.line()
        
        if(abs(line.x1() - line.x2()) > abs(line.y1() - line.y2())):
            
            # Set new line
            self.line.setLine(
                line.x1(),
                line.y1(),
                line.x2(),
                line.y1()
            )
        
        else:
            # Set new line
            self.line.setLine(
                line.x1(),
                line.y1(),
                line.x1(),
                line.y2()
            )
        
        # Early return if it was last line
        if(not changeNextOne): return
        
        nextLine = self.lines[pos + 1]
        
        nextLine.setLine(
            self.line.line().x2(),
            self.line.line().y2(),
            nextLine.line().x2(),
            nextLine.line().y2()
        )
        
    def update(self , Sclass , inputBox):
        self.config[Sclass] = inputBox.text()  
        
        self.pen = QPen()  
        
        self.pen.setColor(QColor(self.config["color"]))
        
        self.pen.setWidth(int(self.config["width"]))
        
        self.line.setPen(self.pen)
        
    def undoHandler(self): 
        self.increase(self.parent.cursor().pos())
                
        self.lines[-1].hide()
        
        self.poped.append(self.lines.pop(-1))
        
        self.line = self.lines[-1]
    
    def showToolTip(self):
        polygon = QPolygonF()
        
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setWidth(2)
        
        for points in [QPoint(100 , 100 - 50) , QPoint(700 , 100 - 50) , QPoint(700 , 160 - 50 - 10) , QPoint(400 , 160 - 50 - 10) , QPoint(390 , 170 - 50 - 10) , QPoint(380 , 160 - 50 - 10) , QPoint(280 , 160 - 50 - 10) , QPoint(100 , 160 - 50 - 10) , QPoint(100 , 100 - 50 + 10)]:
            polygon.append(QPointF(points))
            
        self.tooltip = self.parent.scene().addPolygon(polygon , pen)
        
        self.tooltip.setBrush(QColor("#2E3440"))
        
        pen = QPen()
        
        pen.setColor(QColor("#88C0D0"))
        
        pen.setWidth(-1)
        
        font = QFont("Comfortaa" , 15)
        
        text = QGraphicsSimpleTextItem("Here are your layers, click the layer to customize" , self.tooltip)
        
        text.setBrush(QColor("#88C0D0"))
        
        text.setPen(pen)
        
        text.setFont(font)
        
        rect = text.boundingRect()
        
        bounding = self.tooltip.boundingRect()
            
        rect.moveCenter(QPointF(bounding.center().x() , bounding.center().y() - 5))
        
        text.setPos(rect.topLeft())        
        
        self.tooltip.setPos(QPoint(
            self.lineLayers.width() // 2 - self.tooltip.boundingRect().width() // 2 - 30,
            self.lineLayersParent.pos().y() - 110
        ))
        
        self.tooltip.show()
        
                
    def showHelp(self):
        def run_second():
            self.animation = Animation.fadingAnimation(Animation , self.help , 300)
            
            self.animation.finished.connect(self.help.hide)
            
            self.animation.start()
        
        self.help = QLabel(self.parent)
        
        self.help.setGeometry(self.parent.geometry())
        
        helpLayouts = QVBoxLayout()
        
        helpLayouts.setSpacing(30)
        
        self.details = QLabel()
                
        self.another = QShortcut(QKeySequence("Return") , self.parent)
        
        self.another.activated.connect(self.savePronto)
        
        self.details.setText("1. Press Enter to save and exit \n\n2. Click and drag the mouse to draw line \n\n3. Press Ctrl+X to customize the lines drawn")
        
        self.details.setStyleSheet("background-color: transparent; color: white; font-size: 20px")
        
        helpLayouts.addWidget(self.details , alignment=Qt.AlignBottom | Qt.AlignCenter)
        
        okay = ClickableLabel("Okay" , None)
        
        okay.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        okay.setCursor(Qt.PointingHandCursor)
        
        okay.setStyleSheet("background-color: transparent; border: 1px solid #3B4252")
        
        okay.clicked.connect(run_second)
        
        okay.setFixedSize(200 , 50)
            
        helpLayouts.addWidget(okay , alignment=Qt.AlignTop | Qt.AlignCenter)
        
        self.help.setLayout(helpLayouts)
                
        self.help.setStyleSheet("""
            background-color: rgba(46, 52, 64, 160);
            font-size: 30px;                        
        """)
        
        self.help.show()
        
        self.animation = Animation.fadingAnimation(Animation , self.help , 300 , True)
                
        self.animation.start()
        
    def hideToolTip(self):
        try:
            # self.animation = Animation.fadingAnimation(Animation , self.tooltip , 200)
        
            # self.animation.start()
            pass
        except:
            pass
        
    def savePronto(self):        
        self.lineLayersParent.hide()
        
        self.menu.hide()
        
        try:
            self.tooltip.hide()
        except:
            pass
        
        self.help.hide()
        
        width , height = Image.open(self.dir).size
        
        # Get the geometry
        area = QRect(0 , 0 , width , height)
        
        for line in self.lines:
            opacity = QGraphicsOpacityEffect()
            
            line.setGraphicsEffect(opacity)
            
            opacity.setOpacity(1)
        
        # Parse the image 
        image = QImage(area.size(), QImage.Format_ARGB32_Premultiplied)
        
        painter = QPainter(image)
        
        self.parent.scene().render(painter, QRectF(image.rect()), QRectF(area))
        
        painter.end()
                        
        image.save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png") , quality=100)
        
        self.animation = Animation.fadingAnimation(Animation , self.parent , 200)
        
        self.animation.finished.connect(self.parent.hide)
        
        self.animation.start()
        
        self.renderArea.set_pixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
    
        self.another.setKey(QKeySequence())
        
    def applyAll(self , name):
        for line in self.lines:
            
            pen = line.pen()
            
            if(name == "Width"):
                
                pen.setWidth(int(self.config["width"]))
            
            else:
                
                pen.setColor(QColor(self.config["color"]))
                
            
            line.setPen(pen)
            
    def removePartial(self):
        self.animation = QParallelAnimationGroup()
        
        for line in self.lines:
            self.animation.addAnimation(Animation.fadingAnimation(Animation , line , 200 , True , 0.4))
            
        self.animation.start()

class PolyGon(doodleShape):
    def __init__(self , parent , renderArea , directory):
        super().__init__(parent , renderArea , directory)
        
    def onClick(self, event: QMouseEvent):
        self.initPointLine(event.pos() , True)
        
    def saveDrawing(self , points):
        pass