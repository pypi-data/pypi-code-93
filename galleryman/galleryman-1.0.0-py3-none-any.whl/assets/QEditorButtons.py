# Importing all modules
import shutil
from PIL import Image , ImageQt
from GalleryMan.themes.filters import Filters
from GalleryMan.assets.QtHelpers import PopUpMessage
from PyQt5.QtCore import QPropertyAnimation, Qt
from PyQt5.QtGui import QCursor, QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGraphicsOpacityEffect, QLabel, QPushButton, QVBoxLayout
from GalleryMan.assets.QtImageProcessor import ImageProcessor
import os

# Animation class for unhide and hide
class Animation:
    def fade(self, widget , start=1 , end=0):
        self.effect = QGraphicsOpacityEffect()
        
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        
        self.animation.setDuration(200)
        
        self.animation.setStartValue(start)
        
        self.animation.setEndValue(end)
        
        return self.animation

    def unfade(self, widget , start=0 , end=1):
        self.effect = QGraphicsOpacityEffect()
        
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        
        self.animation.setDuration(200)
        
        self.animation.setStartValue(start)
        
        self.animation.setEndValue(end)
        
        return self.animation


class PaletteView:
    def __init__(self, main_window, image, out_widget , config ) -> None:
        
        # Make all args global        
        self.edited = False
        
        self.config = config
        
        self.out_widget = out_widget
                        
        self.main_window = main_window
        
        # Initialize the image processor class
        self.processors = ImageProcessor()
        
        # Add image
        self.processors.add_image(image)
    

    def blur(self):
        # Make the edited variable True
        self.edited = True
        
        # Animation Callback
        def callback():
            
            # Blur the imahe
            self.out_widget.set_pixmap(self.createPixmap(self.processors.blur()))
            
            # Set pixmap
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            # Partial unhide
            Animation.unfade(Animation , self.out_widget , 0.5).start()
            
        # Partial hide while the image is being processed
        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)
        
        # Call callback on finish
        self.animations.finished.connect(callback)
        
        # Start the animation
        self.animations.start()

    def sharp(self):        
        # Make the edited variable True
        self.edited = True
        
        # Animation Callback
        def callback():
            
            # Blur the imahe
            self.out_widget.set_pixmap(self.createPixmap(self.processors.sharpen()))
            
            # Set pixmap
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            # Partial unhide
            Animation.unfade(Animation , self.out_widget , 0.5).start()
            
        # Partial hide while the image is being processed
        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)
        
        # Call callback on finish
        self.animations.finished.connect(callback)
        
        # Start the animation
        self.animations.start()
        
    def increaseBrightness(self):
        # Make the edited variable True
        self.edited = True
        
        # Animation Callback
        def callback():
            
            # Blur the imahe
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseBrightness()))
            
            # Set pixmap
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            # Partial unhide
            Animation.unfade(Animation , self.out_widget , 0.5).start()
            
        # Partial hide while the image is being processed
        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)
        
        # Call callback on finish
        self.animations.finished.connect(callback)
        
        # Start the animation
        self.animations.start()
        
    def increaseContrast(self):
        # Make the edited variable True
        self.edited = True
        
        # Animation Callback
        def callback():
            
            # Blur the imahe
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseContrast()))
            
            # Set pixmap
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            # Partial unhide
            Animation.unfade(Animation , self.out_widget , 0.5).start()
            
        # Partial hide while the image is being processed
        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)
        
        # Call callback on finish
        self.animations.finished.connect(callback)
        
        # Start the animation
        self.animations.start()
        
    def increaseExposure(self):
        # Make the edited variable True
        self.edited = True
        
        # Animation Callback
        def callback():
            
            # Blur the imahe
            self.out_widget.set_pixmap(self.createPixmap(self.processors.increaseExposure()))
            
            # Set pixmap
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            # Partial unhide
            Animation.unfade(Animation , self.out_widget , 0.5).start()
            
        # Partial hide while the image is being processed
        self.animations = Animation.fade(Animation , self.out_widget , end=0.5)
        
        # Call callback on finish
        self.animations.finished.connect(callback)
        
        # Start the animation
        self.animations.start()
        
    def createPixmap(self , image: Image):
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))
            
        elif  image.mode == "RGBA":
            r, g, b, a = image.split()
            image = Image.merge("RGBA", (b, g, r, a))
            
        elif image.mode == "L":
            image = image.convert("RGBA")

        im2 = image.convert("RGBA")
        
        data = im2.tobytes("raw", "RGBA")
        
        qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
        
        pixmap = QPixmap.fromImage(qim)
        
        return pixmap

class FilterView:
    def __init__(self, main_window, out_widget , scrollArea ,  icons , callback) -> None:
        
        # Make args global
        self.original = scrollArea.width()
        
        self.scrollArea = scrollArea
        
        self.out_widget = out_widget
        
        self.popup = PopUpMessage()
        
        self.animation = Animation()
        
        self.imageProcessor = Filters(Image.open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")).convert("RGBA"))
        
        self.callback = callback
        
        self.edited = False
        
        self.main_window = main_window
    
    def partial_hide(self):
        return Animation.fade(Animation , self.out_widget , 1 , 0.5)
        
    def partial_unhide(self):
        Animation.unfade(Animation , self.out_widget , 0.5).start()
    
    def shady(self):
        
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.shady())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
        
    def sepia(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.sepia())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def cherry(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.cherry())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def underwater(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.underwater())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def purple(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.purple())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def pink(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.pink())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def dark(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.dark())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)

    def clear(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
        
    def realistic(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.realistic())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
    
    def cool_filter(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.cool())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
        
    def clear_filter(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.clear())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
        
    def grayscale(self):
        # Make edited variable true
        self.edited = True
        
        # Animation callback
        def callback():
            
            # Apply effect
            self.image = ImageQt.ImageQt(self.imageProcessor.grayscale())
            
            # Apply the updated pixmap to the render area
            self.out_widget.setPixmap(QPixmap.fromImage(self.image))
            
            self.out_widget.pixmap().save(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
            
            self.partial_unhide()
            
        # partial hide while the image is being processed
        self.animation = self.partial_hide()
        
        # Start the animation
        self.animation.start()
        
        # Callback
        self.animation.finished.connect(callback)
        
    def show_dialog(self , dialog: QDialog , parent , functions):
        self.dialog = dialog
        
        self.dialog.setParent(parent)
        
        # Set up the dialog
        layout = QVBoxLayout()
        
        label = QLabel(text="Do you want to apply the viewed filter?")
        
        label.setAlignment(Qt.AlignCenter)
        
        label.setStyleSheet("""
            QLabel{
                font-size: 20px;
                color: #D8DEE9;
                font-family: "SauceCodePro Nerd Font"
            }                    
        """)
        
        layout.addWidget(label)
        
        self.dialog.setFixedWidth(700)
        
        self.dialog.setFixedHeight(120)
                        
        self.buttons = QDialogButtonBox()
                        
        # Buttons
        for text , func in zip([" Continue Changes" , " Discard Changes"] , functions):            
            button = QPushButton()
                        
            button.clicked.connect(func)          
            
            button.setText(text)
            
            self.buttons.addButton(button , QDialogButtonBox.ActionRole)
            
            button.setFlat(True)
                        
            button.setCursor(QCursor(Qt.PointingHandCursor)) 
                                           
            button.setStyleSheet('font-size: 20px; color: #D8DEE9')
            
        layout.addWidget(self.buttons)
        
        self.dialog.setLayout(layout)
        
        self.dialog.exec_()
        
        return self.dialog
    
    def remove_self(self):
        
        if(self.edited):
            self.show_dialog(QDialog() , self.main_window , [self.useUpdate , self.removeUpdated])
        else:
            self.scrollArea.setFixedWidth(self.original)
            
            self.callback()
            
    def useUpdate(self):
        self.dialog.hide()
        
        self.callback()
                
        shutil.copy(os.path.join("GalleryMan" , "assets" , "currently_edited.png") , os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))
        
        self.out_widget.set_pixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
        
    def removeUpdated(self):
        self.dialog.hide()
        
        self.out_widget.setPixmap(QPixmap(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png")))
        
        self.callback()
    
        os.remove(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "processed_image.png"))