# Import All The Required Modules
from configparser import ConfigParser
import json, os
from functools import partial
from GalleryMan.assets.QtHelpers import Animation, QContinueButton, QCustomButton
from PyQt5.QtCore import (
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QWidget,
)
from GalleryMan.views.folderview import imagesFolder


class QDoublePushButton(QPushButton):
    """A Subclass Of QPushButton, But With A Listener of `Double Click`

    Args:
        parent (QWidget, optional): Parent Widget. Defaults to None.
    """

    doubleClicked = pyqtSignal()

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clicked.emit)
        super().clicked.connect(self.checkDoubleClick)

    @pyqtSlot()
    def checkDoubleClick(self):
        if self.timer.isActive():
            self.doubleClicked.emit()
            self.timer.stop()
        else:
            self.timer.start(250)


class FirstPage:

    def __init__(
        self,
        window: QWidget,
        application: QMainWindow,
        scrollArea: QScrollArea,
        config: ConfigParser,
        topbar: QWidget,
        app
    ) -> None:
        
        self.app = app
        
        self.topbar = topbar

        self.application = application

        self.scrollarea = scrollArea

        self.config = config

        # Defining All The Variables
        self.original_window_size = 0

        self.window = window

        application.resizeEvent = self.responser

        self.frame = QLabel()

        self.main_layout = QHBoxLayout()

        self.isdir_open = False

        self.height = 0

        self.scans = set()

        self.frame.setGeometry(QRect(0, 0, 1980, 500))

        self.main_layout.setSpacing(4)

    def start(self):
        """Starts Creating The UI

        Args:
            window (QMainWindow): The Main Window In Which The Content Will Be Rendered
        """
        #  ___________________________
        # |                           |
        # |    Main Window Settings   |
        # |___________________________|
        #

        # Change Window Name
        self.window.setObjectName("GalleryMan StartUp")

        # GalleryMan Welcome Text
        self.header_text = QLabel(text="Welcome To GalleryMan!", parent=self.window)

        # Center Alignment
        self.header_text.setAlignment(Qt.AlignCenter | Qt.AlignBottom)

        # Set Geometry
        self.header_text.setGeometry(QRect(140, 450, 640, 100))

        # A Push Button To Go To Next Page
        self.next = QCustomButton("Let's Go  ", self.window).create()

        # Set geometry
        self.next.setGeometry(QRect(240, 550, 500, 100))

        # Switch To Pointing hand On Hover 
        self.next.setCursor(QCursor(Qt.PointingHandCursor))

        # Some stylings
        self.next.setStyleSheet(
            """
            QPushButton{
                color: #88C;
                font-family: "Comfortaa";
                font-size: 40px !important;  
            }
        """
        )

        # Let the scrollarea take up all the space
        self.scrollarea.setGeometry(self.application.geometry())

        # Move to next page (directory) on click
        self.next.clicked.connect(self.go_to_next)

        # Add finishing touches
        self.responser(None)
        
        self.application.show()

    def go_to_next(self):
        "Goes to next page, which is the directory selection page"

        # Show the scrollbar
        self.scrollarea.show()

        # Find all the sub directories in the home directory
        home_directories = [".."] + sorted(os.listdir(os.path.expanduser("~")))

        # Set the height of the directories as the number of sub directories
        self.window.setMinimumHeight(14 * len(home_directories))

        # Make the dir open (used while resizing)
        self.isdir_open = True

        # Hide the text button
        self.next.hide()

        # Create animation for the header text which will be changed
        self.animation = Animation.fadingAnimation(Animation, self.header_text, 500)

        # Start the animation
        self.animation.start()

        # Call next function on completion of the animation
        self.animation.finished.connect(partial(self.next_animation , home_directories))

    def next_animation(self, home_directories):

        # Change the hader text
        self.header_text.setText("Choose The Directories Which Should Not Be Scanned")

        # Set some stylings
        self.header_text.setStyleSheet("font-size: 35px")

        # Change parent
        self.header_text.setParent(self.window)

        # More info on the current page under the header_text
        self.more_text = QLabel(
            text="(Preventing Directories Which Doesn't Contain Images Makes The App Faster)",
            parent=self.window,
        )

        # Geometry and some stylings
        self.more_text.setGeometry(QRect(550, 100, 1980, 100))

        self.more_text.setStyleSheet("font-size: 20px")

        # Show the label
        self.more_text.show()

        # Parallel animation
        self.animation = QParallelAnimationGroup()

        # Unhide the header_text
        self.animation.addAnimation(
            Animation.fadingAnimation(Animation, self.header_text, 500, reverse=True)
        )

        # Move the header text to up
        moving_animation = QPropertyAnimation(self.header_text, b"pos")

        moving_animation.setDuration(500)

        moving_animation.setStartValue(QPoint(0, 80))

        moving_animation.setEndValue(QPoint(0, 0))

        self.animation.addAnimation(moving_animation)

        # Start the animation
        self.animation.start()

        # A Label for showing directories
        self.directoriesLabel = QLabel(self.window)

        # Set geometry
        self.directoriesLabel.setGeometry(QRect(0, 0, 1980, 5000))

        # Enable scrollbars
        self.scrollarea.verticalScrollBar().setEnabled(True)

        self.scrollarea.verticalScrollBar().show()

        # Hardcoding postion for each sub directory
        y = 100

        # Iterate through all the directories
        for dir in home_directories:
            # Check if the folder is not a private one and is not a file
            if (dir[0] != "." or dir == "..") and os.path.isdir(
                os.path.join(os.path.expanduser("~") , dir)
            ):

                # Create a double clickable push button
                name = QDoublePushButton(self.directoriesLabel)

                # Change the cursor
                name.setCursor(QCursor(Qt.PointingHandCursor))

                # Set it flat, no borders required
                name.setFlat(True)

                # Some stylings
                name.setStyleSheet(
                    "font-size: 22px; font-family: SauceCodePro Nerd Font"
                )

                # Move to the desired position
                name.move(QPoint(0, y))

                # A custom icon at teh left of the name of the folder
                if "download" in dir.lower():
                    text = "  " + dir
                elif "desktop" in dir.lower():
                    text = "  " + dir
                elif "google" in dir.lower() and "drive" in dir.lower():
                    text = "  " + dir
                elif "picture" in dir.lower():
                    text = "  " + dir
                elif os.path.islink(dir):
                    text = "  " + dir
                else:
                    text = "  " + dir

                # Get the total number of sub folders inside the parent folder
                files, total_folders = self.get_info(
                   os.path.join(os.path.expanduser("~") , dir)
                )
                
                # Add that beside the folder name
                text += " ({} images | {} folders | {}Kb)".format(
                    files,
                    total_folders,
                    os.path.getsize(os.path.join(os.path.expanduser("~") , dir)),
                )

                # Set the text
                name.setText(text)

                # Update dirs with the inner directories on double click
                name.doubleClicked.connect(
                    partial(self.update_dirs, os.path.join(os.path.expanduser("~") , dir))
                )

                if dir != "..":
                    # Unselect the folder on click
                    name.clicked.connect(
                        partial(self.select, os.path.join(os.path.expanduser("~") , dir), name)
                    )

                y += 70

        # Finally, move to the folder page
        self.continue_to_next = QContinueButton(self.window).start()

        # Show the button
        self.continue_to_next.show()

        # Some styles
        self.continue_to_next.setStyleSheet(
            "font-size: 20px; background-color: #2E3440;"
        )

        # Set geometry
        self.continue_to_next.setGeometry(
            QRect(
                self.window.size().width() + 100,
                self.window.size().height() + 100,
                200,
                100,
            )
        )

        # Transfer control to the folder page
        self.continue_to_next.clicked.connect(self.transfer_control)

        # Add finishing touches
        self.update_sizes(self.window.geometry())

        # Show the label
        self.directoriesLabel.show()

    def transfer_control(self):
        # Write all the directories that are prevented by the user to read
        with open(os.path.join(os.path.expanduser("~") , ".galleryman" , "data" , "scan_dirs.txt"), "w") as file:
            file.write(json.dumps(list(self.scans)))

        # Hide all the widgets that are not required
        self.directoriesLabel.hide()

        self.header_text.hide()

        self.continue_to_next.hide()

        self.more_text.hide()

        try:
            self.new_dirs.hide()

            del self.new_dirs
        except:
            pass

        self.scrollarea.verticalScrollBar().setValue(0)

        # Remove all the unused variables
        del self.directoriesLabel, self.continue_to_next, self.more_text

        # Call the main class
        imagesFolder(self.window, self.application, self.scrollarea, self.config , self.topbar , self.app).start(self.header_text)

    def update_dirs(self, directory: str):
        """Updates the directories label with the new directory

        Args:
            directory (str): Path of the directory
        """

        # Check if the new directory
        try:
            self.new_dirs.hide()
        except:
            pass

        # Move the scrollbar to top
        self.scrollarea.verticalScrollBar().setValue(0)

        # Hide the diretory label
        self.directoriesLabel.hide()

        # Create a new directory label
        self.new_dirs = QLabel(self.window)

        # Set geometry
        self.new_dirs.setGeometry(self.directoriesLabel.geometry())

        # Again, hardcoding positions
        y = 100

        # Iterate through all the sub directories
        for dir in [".."] + os.listdir(directory):

            # Check if the path is a folder
            if not os.path.isdir(os.path.join(directory , dir)) or (
                dir[0] == "." and dir != ".."
            ):
                continue

            # Create a button
            name = QDoublePushButton(self.new_dirs)

            # Set cursor
            name.setCursor(QCursor(Qt.PointingHandCursor))

            # Make that flat
            name.setFlat(True)

            # Some stylings
            name.setStyleSheet("font-size: 20px; font-family: SauceCodePro Nerd Font")

            # Custom folder icon
            if "download" in dir.lower():
                text = "  " + dir
            elif "desktop" in dir.lower():
                text = "  " + dir
            elif "google" in dir.lower() and "drive" in dir.lower():
                text = "  " + dir
            elif "picture" in dir.lower():
                text = "  " + dir
            elif os.path.islink(dir):
                text = "  " + dir
            else:
                text = "  " + dir

            # Get total number of files and images in the directory
            files, total_folders = self.get_info("{}/{}".format(directory, dir))

            # Add it to the text
            text += " ({} images | {} folders | {}Kb)".format(
                files, total_folders, 1980
            )

            # Set the text
            name.setText(text)

            # Remove all the slashes and ..(s)
            if os.path.normpath(os.path.join(os.path.expanduser("~") , dir)) in self.scans:

                # Make it a little light (or transparent) if it is selected
                self.opacity = QGraphicsOpacityEffect()

                self.opacity.setOpacity(0.5)

                name.setGraphicsEffect(self.opacity)

            # Update the directories on click (recursion)
            name.doubleClicked.connect(partial(self.update_dirs, os.path.join(os.path.expanduser("~") , dir)))

            # Select the folder on click if it is not the parent folder
            if dir != "..":
                name.clicked.connect(partial(self.select, os.path.join(os.path.expanduser("~") , dir), name))

                # Move to desired location
            name.move(QPoint(0, y))

            # Show the label
            name.show()

            # UOdate the postion
            y += 65

        # Show the directory
        self.new_dirs.show()

    def select(self, directory, label):

        # Remove all unnecessary slashes and dots
        directory = os.path.normpath(directory)

        # Check if is already there, then unselect
        if directory in self.scans:            
            self.animation = Animation.fadingAnimation(Animation , label, 200 , startValue=0.5 , reverse=True)
            
            self.animation.start()

            self.scans.remove(directory)

        else:
            self.animation = Animation.fadingAnimation(
                Animation, label, 200, endValue=0.5
            )
            
            self.animation.start()

            self.scans.add(directory)

    def responser(self, _):
        self.update_sizes(self.application.size())
                
    def update_sizes(self, point: QSize):        
        width = point.width()

        height = point.height()
    
        self.window.setGeometry(self.application.geometry())

        self.header_text.setGeometry(0, (height // 2) - 130, width, 100)

        self.next.setGeometry(QRect(0, (height // 2) - 10, width, 100))

        if self.isdir_open:
            self.header_text.setGeometry(0, 10, width, 100)

            self.directoriesLabel.setGeometry(
                (width // 2) - 200, 200, 700, self.directoriesLabel.height()
            )

            self.more_text.setFixedWidth(width)

            self.more_text.move(QPoint(0, 100))

            self.more_text.setAlignment(Qt.AlignCenter)

            self.continue_to_next.move(
                QPoint(
                    self.window.size().width() - 200, self.window.size().height() - 100
                )
            )

    def get_info(self, dir):
        files = 0

        sub_folders = 0

        for i in self.generator(dir):
            files += i[-3:] in ["png", "svg", "jpeg", "jpg"]

            if os.path.isdir(os.path.join(dir , i)):
                sub_folders += 1

        return [files, sub_folders]

    def generator(self, dir):
        for i in os.listdir(dir):
            yield i
