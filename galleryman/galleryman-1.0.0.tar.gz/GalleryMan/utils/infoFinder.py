from PyQt5.QtGui import QKeySequence, QPixmap
from GalleryMan.assets.QtHelpers import Animation, PopUpMessage
import os
from PIL import Image
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QLabel, QLineEdit, QShortcut, QVBoxLayout


class getMoreInfo:
    def __init__(self , scrollArea , renderArea , directory , application) -> None:
        
        # Make every arg global
        self.renderArea = renderArea
        
        self.scrollArea = scrollArea
        
        self.directory = directory
        
        self.application = application
        
        self.message = PopUpMessage()
        
        self.image = Image.open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
    def getInfo(self):
        
        # To prevent recreation of the parent over the widget, it would be better to hide the prent before hand
        try:
            self.animation = Animation.fadingAnimation(Animation , self.parent , 100)
            
            self.animation.finished.connect(self.parent.hide)
            
            self.animation.start()
            
        except Exception as e:
            pass
        
        # Check if the rename option is not opened
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 100)
            
            self.animation.finished.connect(self.renameParent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        # Create a label 
        self.parent = QLabel(self.renderArea)
        
        # Set a special property to prevent addition of the border on the child labels
        self.parent.setProperty("class" , "need")
        
        # Set geometry
        self.parent.setGeometry(self.renderArea.geometry())
        
        # Stylings
        self.parent.setStyleSheet("""
            QLabel[class="need"]{{
                background-color: #2E3440; 
            }}
        """)
                
        # Create a layout which would hold every child labels
        layout = QVBoxLayout()
        
        # File path child
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Path: {}".format(self.directory))
        
        layout.addWidget(filePath)
        
        # File name child
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Name: {}".format(self.directory[self.directory.rindex("/") + 1:]))
        
        layout.addWidget(filePath)
        
        width , height = Image.open(self.directory).size
        
        
        # Resolution child
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("Resolution: {} x {}".format(width , height))
        
        layout.addWidget(filePath)
                
        bytesSize = os.path.getsize(self.directory)
        
        # File size child
        filePath = QLabel()

        filePath.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
        """)

        filePath.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        filePath.setText("File Size: {} bytes ({} MB)".format(bytesSize , round(bytesSize / 1e+6 , 2)))
        
        layout.addWidget(filePath)
        
        # Set the widget
        self.parent.setLayout(layout)
        
        # Show the parent
        self.parent.show()
    
    def castToScreen(self):
        pass
    
    def searchGoogle(self):
        pass
    
    def showInFullScreen(self):
        self.graphics = QGraphicsView(self.application)

        self.graphics.setGeometry(QRect(0 , 0 , 1980 , 1080))
        
        self.graphics.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scene = QGraphicsScene()
        
        self.graphics.setScene(self.scene)
                
        self.graphics.show()
        
        self.scene.addPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")).scaled(self.application.geometry().width() , self.application.geometry().height() , transformMode=Qt.SmoothTransformation))
        
        self.graphics.show()
            
    def rename(self):
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 100)
            
            self.animation.finished.connect(self.renameParent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        try:
            
            self.animation = Animation.fadingAnimation(Animation , self.parent , 100)
            
            self.animation.finished.connect(self.parent.hide)
            
            self.animation.start()
            
        except:
            
            pass
        
        # Create a label which will hold the text edit
        self.renameParent = QLabel(self.renderArea)
        
        self.renameParent.setProperty("class" , "need")
        
        # New message
        self.message.new_msg(self.application , "Press Enter To Rename File" , 400)
        
        # Listen for Enter click events
        key = QShortcut(QKeySequence("Return") , self.renameParent)
        
        # Save the photo with a new filename on click 
        key.activated.connect(self.saveWithNew)
        
        # Set geometry
        self.renameParent.setGeometry(self.renderArea.geometry())
        
        # Stylings
        self.renameParent.setStyleSheet("""
            QLabel[class="need"]{{
                background-color: #2E344050;
            }}
        """)
        
        # Layout which will hold text edit
        layout = QVBoxLayout()
        
        # Input box
        self.inputBox = QLineEdit()
        
        # Sized
        self.inputBox.setFixedHeight(50)
        
        self.inputBox.setFixedWidth(1000)
        
        # Placeholder
        self.inputBox.setPlaceholderText("New file name: ")
        
        # Stylings
        self.inputBox.setStyleSheet("""
            color: #D8DEE9;
            font-size: 20px;
            font-family: Comfortaa                       
        """)
        
        # Alignment
        self.inputBox.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        
        # Add to layout
        layout.addWidget(self.inputBox , alignment=Qt.AlignCenter | Qt.AlignCenter)
        
        # Set layout
        self.renameParent.setLayout(layout)
        
        # Show the label
        self.renameParent.show()
    
    def callback(self):
        pass
    
    def saveWithNew(self):
        try:
            self.image.save(self.inputBox.text())
            
            self.animation = Animation.fadingAnimation(Animation , self.renameParent , 300)
            
            self.animation.start()
            
        except:
            self.message.new_msg(self.application , "Invalid File Extension" , 400)