# Importing all the required modules
from pathlib import Path
from GalleryMan.assets.editorButtonsHelper import QEditorHelper
from math import ceil
import functools, json
from configparser import ConfigParser
from random import randint
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage, QCustomButton
from PyQt5.QtCore import (
    QAbstractAnimation,
    QObject,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QThread,
    QVariant,
    QVariantAnimation,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QCursor, QMouseEvent, QPixmap, QTransform
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QWidget,
)
import os
import shutil

class FindAll(QObject):
    # Signals and slots
    finished = pyqtSignal()
    
    curr = pyqtSignal(int , str)
    
    request_label = pyqtSignal(str)
    
    label = None

    def run(self , inst , dirs , card_width , card_height , padding , color_mode , colors , x , y):
        # A variable to keep track of the number of cards
        done = 0
        
        for i in dirs:     
            
            # Make the accepted variable false
            self.accepted = False
            
            # Parse to sring
            i = str(i)
            
            # Check if the image is a supported format
            if os.path.isdir(i) or i[-3:] not in [
                "png",
                "jpg",
                "jpeg",
            ]:
                continue
                        
            # Add done
            done = done + 1
            
            # Get first 50 letters of the path
            temp = i[:50] + '...' if len(i) > 50 else i
            
            # Send the number of uimages parsed and current parsing image to the signal
            self.curr.emit(done , temp)
            
            # Request label
            self.request_label.emit(i)
            
            # Wait while the request is accepted
            while not self.accepted:
                self.test = True
            
            # Create the card
            self.final(inst , i , card_width , card_height , padding , color_mode , colors , x , y)
            
            # Update x and y pos
            x += card_width + padding
            
            if x > inst.application.size().width() - 250:
                x = 40

                y += card_height + padding

        
        # Add finishing touches
        inst.responser(None)
        
        # Emit the finish signal
        self.finished.emit()
            
    def final(self , inst , i , card_width , card_height , padding , color_mode , colors , x , y):                       
        # Create pixmap        
        MakePixmap().run(i , card_width , card_height , self.label)
        
        # Check for color mode
        if color_mode == "single":
            inst.index = 0
        elif color_mode == "random":
            inst.index = randint(0, len(colors) - 1)
        else:
            inst.index = (inst.index + 1) % len(colors)

        # Set geomerty
        self.label.setGeometry(QRect(0, 0, card_width, card_height))
        
        # Use Pointing cursor on hover
        self.label.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Use border accordingly
        self.label.setStyleSheet(
            "border: {}px solid {}".format(
                inst.config.get("singleFolder" , "card-borderWidth"),
                colors[inst.index]
            )
        )
        
        # Call a function on click
        self.label.clicked.connect(functools.partial(inst.show_image, i))
        
        # Move to correct x and y pos
        self.label.move(QPoint(x, y))
        
        # Add to folder list
        inst.folders.append(self.label)
        
        

class MakePixmap(QObject):    
    finished = pyqtSignal()
        
    def run(self , dir , card_width , card_height , parent):        
        pixmap = QPixmap(dir).scaled(card_width , card_height , transformMode=Qt.SmoothTransformation)
                
        parent.setPixmap(pixmap)
        
        self.finished.emit()

class CustomLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def __init__(self, parent=None , listenFor = Qt.LeftButton):
        super().__init__(parent=parent)
        
        self.listenFor = listenFor

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Listen for click on label
        if event.button() == self.listenFor:
            self.clicked.emit(event.pos())
            
            self.eventPos = event.pos()


class QRotateLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(QRotateLabel, self).__init__(*args, **kwargs)
        self._pixmap = QPixmap()

        self.curr = 0

        self.initial = 0

        self.init_ani()

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


class singleFolderView():
    LIKED_FOLDERS = os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "likedFolders.txt")
    
    def init(
        self,
        window: QWidget,
        directory: str,
        config: ConfigParser,
        scroll: QScrollArea,
        application: QMainWindow,
        app: QApplication,
        topbar: QLabel,
        panel: QLabel,
        *args
    ) -> None:
        self.panel = panel
        
        self.topbar = topbar
        
        self.app = app
        
        self.scroll = scroll
        
        self.scroll.verticalScrollBar().setEnabled(True)

        self.scroll.verticalScrollBar().show()

        self.application = application

        self.window = window
        
        self.original = self.window.geometry()
        
        self.original_responser = self.application.resizeEvent
        
        self.config = config

        self.application.resizeEvent = self.responser

        self.folders = []

        self.args = args

        self.popup = PopUpMessage()
                
        if(directory != None):
        
            self.name = QLabel(self.window)
            
            geometry = QRect(self.args[0].geometry())
            
            geometry.setY(0)

            self.name.setGeometry(geometry)
                        
            if(directory != self.LIKED_FOLDERS):
                self.name.setText(directory[directory.rindex("/") + 1 :])
            else:
                self.name.setText("Favourites")

            self.name.setAlignment(Qt.AlignCenter)

            self.name.show()

            self.name.setStyleSheet(
                "color: {}; font-family: {}; font-size: {}; ".format(
                    self.config.get("singleFolder", "headerText-color"),
                    self.config.get("singleFolder", "headerText-fontFamily"),
                    self.config.get("singleFolder", "headerText-fontSize") + "px",
                )
            )

        self.directory = directory
        
        self.copy = directory
        
        self.config = config
        
        self.start()

    def remove_self(self):
        # A Parallel Animation class
        self.animation = QParallelAnimationGroup()
        
        # Hide opened image
        try:
            self.main_window.hide()
            
            self.central.hide()
        except:
            pass
        
        # Hide folder's name
        try:
            self.name.hide()
            
            self.new_label.hide()
        except Exception as e:
            pass
        
        # Reset everything
        try:
            for i in [self.labelArea, self.name, self.go_back]:
                self.animation.addAnimation(Animation.fadingAnimation(Animation , i , 200))

        except Exception as e:
            pass
            
        for i in self.args:
            i.show()

            self.animation.addAnimation(
                Animation.fadingAnimation(Animation, i, 200, True)
            )

        self.window.setGeometry(self.original)
        
        
        self.scroll.setGeometry(self.original)
        
        self.scroll.verticalScrollBar().setValue(0)
        
        self.application.resizeEvent = self.original_responser
        
        self.application.resizeEvent(None)
        
        self.animation.start()

        self.animation.finished.connect(self.remove)

    def remove(self):
        
        # Hide and delete unused variable and collect garbage
        self.labelArea.hide()

        self.animation = self.main_window = self.labelArea = self.name = None

        del self.animation, self.main_window, self.labelArea, self.name

    def start(self):
        
        # Get the back button text
        self.go_back = QCustomButton(
            text=self.config.get("singleFolder", "back-buttonText")[1:-1],
            window=self.window,
        ).create()
        
        # Stylings
        self.go_back.setStyleSheet(
            """
            font-size: {}px;
            font-family: {};    
            color: {};                 
        """.format(
                self.config.get("singleFolder", "back-buttonFontSize"),
                self.config.get("singleFolder", "back-buttonFontFamily"),
                self.config.get("singleFolder", "back-buttonColor"),
            )
        )
        
        # Geometry
        self.go_back.setGeometry(
            QRect(
                int(self.config.get("singleFolder", "back-buttonTopPadding")),
                int(self.config.get("singleFolder", "back-buttonLeftPadding")),
                int(self.config.get("singleFolder", "back-buttonWidth")),
                int(self.config.get("singleFolder", "back-buttonHeight")),
            )
        )
        
        # Go back key bindings
        self.go_back.setShortcut("Alt+Left")
        
        # Call the function
        self.go_back.clicked.connect(self.remove_self)
        
        # Show
        self.go_back.show()
        
        # Area where images will be rendered
        self.labelArea = QLabel(self.window)
        
        # Hide for a while
        self.labelArea.hide()
        
        # Geometry
        self.labelArea.setGeometry(QRect(0, 150 , self.application.width() , self.application.height()))
        
        # Get card properties
        padding = int(self.config.get("singleFolder", "card-padding"))

        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        colors = json.loads(self.config.get("singleFolder", "card-color"))

        color_mode = json.loads(self.config.get("singleFolder", "card-mode"))

        self.index = 0

        
        # Set a waiting cursor
        self.application.setCursor(Qt.BusyCursor)
        
        # Default x and y
        x, y = 40, 100
                
        # Check if the clicked directory is of liked photes
        if(self.copy == os.path.join(os.path.expanduser('~') , ".galleryman" , "data" , "likedFolders.txt")):
            with open(os.path.join(os.path.expanduser('~') , ".galleryman" , "data" , "likedFolders.txt") , "r") as file:
                dirs = json.loads(file.read())
                
            
                
            # Filter all the deleted images which were in the liked Folders
            dirs = list(filter(lambda x: os.path.isfile(x) , dirs))
            
            # Update the file
            with open(os.path.join(os.path.expanduser('~') , ".galleryman" , "data" , "likedFolders.txt") , "w") as file:
                file.write(json.dumps(dirs))
            
                
        else:
            try:
                dirs = Path(self.copy).rglob("*")
            except:
                dirs = []
        
        # A loader which will show the track of processing
        self.loader = QLabel(self.application)
        
        # Cover the whole area
        self.loader.setGeometry(self.application.geometry())
        
        # Set text
        self.loader.setText("Loaded 0 images \n\n Starting")
        
        # Some stylings
        self.loader.setStyleSheet("""
            QLabel{
                color: #88C0D0;
                font-family: "SauceCodePro Nerd Font";
                font-size: 30px;
            }                      
            """)
        
        # Alignment
        self.loader.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        # Show
        self.loader.show()
        
        # Thread which will process
        self.thread = QThread(self.application)
        
        self.worker = FindAll()
        
        self.worker.moveToThread(self.thread)
        
        self.worker.curr.connect(self.update)
                
        self.thread.started.connect(functools.partial(self.worker.run , self , dirs , card_width , card_height , padding , color_mode , colors , x , y))
        
        # Send label on request
        self.worker.request_label.connect(self.sendLabel)
        
        # Quit thread on finish
        self.worker.finished.connect(self.thread.quit)
        
        # Additional finishing touches
        self.worker.finished.connect(self.finish)
        
        # Start
        self.thread.start()
        
        # Reswitch to Arrow Cursor
        self.application.setCursor(Qt.ArrowCursor)
    
    def finish(self):
        # Change the loader text to Done (yay)
        self.loader.setText("   DONE")
        
        # Animation to show every element with a animation
        self.animations = QParallelAnimationGroup()
        
        self.animations.addAnimation(Animation.fadingAnimation(Animation , self.loader , 200))
        
        self.animations.addAnimation(Animation.fadingAnimation(Animation , self.labelArea , 200 , True))
        
        # Show all the elements on finish
        self.animations.finished.connect(self.labelArea.show)
        
        self.animations.finished.connect(self.loader.hide)
        
        # Call the responser for finishing touches
        self.animations.finished.connect(functools.partial(self.responser , None))
                
        # Start the animation
        self.animations.start()
        
    def update(self , num , s):
        
        # Update the loader text with new data
        self.loader.setText("Loaded {} images \n\n Loading {}".format(num , s))
        
    def sendLabel(self , dir):        
        
        # Create a clickable label        
        label = CustomLabel(self.labelArea)
        
        # Call the show image function on click
        label.clicked.connect(functools.partial(self.show_image , dir))
        
        # Set the worker's label
        self.worker.label = label
        
        # Set to accepted
        self.worker.accepted = True
    
    def show_image(self, name , pos , showOnlyImage=False):
        self.showOnlyImage = showOnlyImage
        
        if(self.showOnlyImage == True):
            self.loader.hide()
        
        # Create copies of directory
        self.origin = name

        self.directory_name = name

        # Center Area (Main)
        self.main_window = QLabel(self.application)

        # Set Geometry        
        self.main_window.move(QPoint(0 , 50))
        
        self.main_window.setFixedSize(self.application.size())

        # QLabel for image
        self.image = QRotateLabel(self.main_window)

        self.dimension = json.loads(
            self.config.get("singleFolder", "editor-imagePadding")
        )

        self.geometry = [
            *self.dimension[:2],
            self.application.size().width() - self.dimension[0] - self.dimension[2],
            self.application.size().height() - self.dimension[1] - self.dimension[3],
        ]

        # Set The Geometry
        self.image.setGeometry(QRect(*self.geometry))

        self.image.setStyleSheet("background-color: transparent")

        shutil.copy(self.directory_name , os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        # Set The Pixmap
        self.pixmap = QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))

        self.image.set_pixmap(self.pixmap)

        self.image.setScaledContents(True)
        
        # Buttons area
        self.central = QLabel(self.application)
        
        # Geomerty
        self.central.setGeometry(QRect(450, 850, 1010, 140))
        
        # Show 
        self.central.show()
        
        # Create layout 
        layout = QHBoxLayout(self.central)
        
        # Add scrollarea to it
        self.scrollArea = QScrollArea(self.central)
        
        layout.addWidget(self.scrollArea)
        
        # Buttons label
        self.buttons = QWidget(self.main_window)
        
        # Set geomerty
        self.buttons.setGeometry(QRect(0, 850, 900, 100))
        
        # Set the scrollarea widget
        self.scrollArea.setWidget(self.buttons)
        
        # Inner button layout
        second_layout = QHBoxLayout(self.buttons)
        
        # Set layout
        self.buttons.setLayout(second_layout)

        # Set fixed spacing between the elements
        second_layout.setSpacing(1)
        
        # Get preffered icons
        self.icons = json.loads(self.config.get("singleFolder", "editorButtons-icons"))

        i = 0
        
        # Main helper class
        self.functional = QEditorHelper(self.app , self.application , self.central , self.config , self.scrollArea , self.image , self.main_window.hide , name)
                
        # respective functions
        functions = [
            lambda : self.functional.copyToClipboard(self.origin),
            lambda : self.functional.showEditButtons(self.origin),
            lambda : self.functional.addtoLiked(self.directory_name , self),
            lambda : self.functional.moveToTrash(self.origin),
            lambda : self.functional.moreInfo(self.directory_name),
            lambda : self.functional.closeWithSave(name)
        ]
        
        
        self.heartWidget = 2
        
        self.isHeartWidgetParsed = False
        
        with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "likedFolders.txt")) as file:
            dirs = json.loads(file.read())
            
        self.stylingForWidget = False
            
        # Iterate through each icon
        for icon, icon_color, icon_font_size, icon_family in self.icons:
            
            # Create a custom redefined label with styling
            item = QCustomButton(icon, self.application, True).create()
                    
            if(self.heartWidget == 0):
                self.heartWidget = item
                
                self.iconStyles = [icon_color , icon_font_size , icon_family]
                
            elif(type(self.heartWidget) == int):

                self.heartWidget -= 1
                
            # Stylings
            if(name in dirs and not self.stylingForWidget and type(self.heartWidget) == QPushButton):
                item.setStyleSheet(
                    "color: {}; font-size: {}px; font-family: {}".format(
                        '#BF616A', icon_font_size, icon_family
                    )
                )
                
                self.stylingForWidget = True
            else:
                item.setStyleSheet(
                    "color: {}; font-size: {}px; font-family: {}".format(
                        icon_color, icon_font_size, icon_family
                    )
                )
                                
            # Connect to the function
            item.clicked.connect(functions[i])
            
            # Increase i
            i += 1
            
            # Add to layout
            second_layout.addWidget(item)
            
                    
        del icon, icon_color, icon_family, icon_font_size, self.pixmap

        self.new_layout = second_layout

        self.main_window.show()

        self.responser(None)
        
    def callback(self):
        def finish():
            self.scrollArea.takeWidget()

            self.scrollArea.setWidget(self.buttons)

        self.ani = QParallelAnimationGroup()

        self.ani.addAnimation(Animation.fadingAnimation(Animation, self.new_label, 200))

        self.ani.addAnimation(
            Animation.fadingAnimation(Animation, self.buttons, 200, True)
        )

        self.ani.start()

        self.ani.finished.connect(finish)

    def responser(self, _):     
        
        # Get required files   
        self.width = self.application.size().width()
        
        try:
            self.main_window.setFixedSize(self.application.size())
        except:
            pass

        card_width = int(self.config.get("singleFolder", "card-width"))

        card_height = int(self.config.get("singleFolder", "card-height"))

        card_padding = int(self.config.get("singleFolder", "card-padding"))
        
        # Default x and y pos
        x, y = 40, 100
        
        # Parallel animation class to run all animations together
        self.animations = QParallelAnimationGroup()
        
        # Iterate through all the items 
        for i in self.folders:
            
            # Move the card to the desired location
            ani = QPropertyAnimation(i, b"pos")

            ani.setStartValue(i.pos())

            ani.setEndValue(QPoint(x, y))

            ani.setDuration(100)
            
            # Update x and y positions
            x += card_width + card_padding

            self.animations.addAnimation(ani)

            if x > self.width - card_width:
                x = 40

                y += card_height + card_padding
                
        # Check how many cards can fit in one line
        self.perline = max((self.width - card_width) // card_width , 1)

        try:
            self.new_width = (50 / 100) * self.width
            
            # Get the new width and set to the central
            self.central.setGeometry(
                QRect(
                    self.new_width // 2,
                    self.application.height() - 150,
                    self.new_width,
                    self.central.height(),
                )
            )
            
            
        except:
            pass
        
        try:
            self.scrollArea.show()
        except:

            pass
        
        # Get the height
        self.height = 300 + (card_height + card_padding) * (ceil(len(self.folders) / self.perline))
        
        # Set the height
        self.window.setFixedHeight(self.height)
    
        try:
            self.labelArea.setFixedHeight(self.height)
        except:
            pass    
        
        try:
            self.geometry = [
                *self.dimension[:2],
                self.application.size().width() - self.dimension[0] - self.dimension[2],
                self.application.size().height()
                - self.dimension[1]
                - self.dimension[3],
            ]

            # Set The Geometry
            self.image.setGeometry(QRect(*self.geometry))

        except:

            pass
        
        # Set additional sizes
        try:
            self.name.setFixedWidth(self.width)

            self.name.setAlignment(Qt.AlignCenter)
        except:
            pass
        
        self.topbar.move(QPoint(self.application.width() - 200 , 0))
        
        self.panel.hide()
        
        self.topbar.setParent(self.application)

        self.animations.start()
