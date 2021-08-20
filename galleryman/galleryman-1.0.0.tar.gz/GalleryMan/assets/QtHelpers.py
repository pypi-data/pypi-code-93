from functools import partial
from PyQt5 import QtCore
from PyQt5.QtCore import QParallelAnimationGroup, QPoint, QPropertyAnimation, QRect, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget


class Thrower:
    """This function does indeed works on a fixed font size, so this has been excluded for the time being."""
    def __init__(self, x, y, window) -> None:
        self.x = x - 10
        self.y = y
        self.window = window

    def fade(self, widget):
        self.effect = QGraphicsOpacityEffect()

        widget.setGraphicsEffect(self.effect)

        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")

        self.animation.setDuration(500)

        self.animation.setStartValue(1)

        self.animation.setEndValue(0)

        return self.animation

    def throw(self):

        animations = QParallelAnimationGroup()

        self.labels = []

        self.blurs = QParallelAnimationGroup()
        
        for left, right in zip(
            [self.x - 40, self.x + 40, self.x ],
            [self.y - 65, self.y - 65, self.y + 35],
        ):
            label = QLabel(self.window)

            label.setText("  ")
            
            label.setStyleSheet("background-color: transparent; font-family: SauceCodePro Nerd Font; color: #BF616A")
            
            label.setFixedHeight(200)

            animation = QPropertyAnimation(label, b"pos")

            animation.setStartValue(QPoint(self.x, self.y))

            animation.setEndValue(QPoint(left, right))

            animation.setDuration(500)

            animations.addAnimation(animation)

            blur_animation = self.fade(label)

            self.blurs.addAnimation(blur_animation)

            label.show()

            self.labels.append(label)

        q = QPushButton(self.window)

        q.clicked.connect(partial(self.start, animations))

        q.click()

    def start(self, animations: QParallelAnimationGroup):
        animations.start()
        
        def callback():
            for i in self.labels:
                i.hide()
        
        animations.finished.connect(callback)

        self.blurs.start()


class QCustomButton:
    """Creates A Push Button With Some Tunings"""

    def __init__(self, text, window , setStyle = False , addtext = None) -> None:
        self.text = text
        
        self.window = window
        
        self.setStyle = setStyle
    
    def create(self):        
        self.button = QPushButton(self.window)
                
        if(self.setStyle):
            self.button.setStyleSheet('font-size: 80px')

        self.button.setFlat(True)

        self.button.setText(self.text)

        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        
        return self.button

class PopUpMessage:            
    def new_msg(self , window , msg , duration):        
        self.window = window
        
        if(type(self.window) != QMainWindow):
            self.window = self.window.parent().parent().parent().parent()
                    
        try:
            self.popup_window.hide()
        except:
            pass
        
        self.popup_window = QLabel(self.window)
                
        self.popup_window.setFixedWidth(len(msg) * 20)
                
        self.popup_window.setFixedHeight(60)
        
        self.popup_window.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
                
        self.popup_window.setText(msg)
        
        self.popup_window.setStyleSheet(
            """
                QLabel{
                    background-color: #4C566A;
                    font-size: 20px;
                    font-family: "Comfortaa"
                }
            """    
        )
        
        self.animation = QPropertyAnimation(self.popup_window, b"pos")

        self.animation.setStartValue(QPoint(20, self.window.height() + 100))
        

        self.animation.setEndValue(QPoint(20, self.window.height() - 100))

        self.animation.setDuration(duration)
    
        self.popup_window.show()
        
        timer = QTimer(self.window)
        
        timer.timeout.connect(self.remove)
        
        timer.start(2000)
        
        self.start()
        
        return self.popup_window
        
        
    def start(self):
        self.animation.start()
        
    def updateText(self , text):
        self.popup_window.setText(text)
        
    def remove(self):
        self.an = QPropertyAnimation(self.popup_window, b"pos")

        self.an.setStartValue(self.popup_window.pos())

        self.an.setEndValue(QPoint(20, 1000))

        self.an.setDuration(200)
            
        self.an.start()
        
        self.an.finished.connect(self.popup_window.hide)
        
class QContinueButton:
    def __init__(self , window) -> None:
        self.window = window
    
    def start(self , text="Continue"):
        self.button = QPushButton(self.window)
        
        self.button.setFlat(True)
        
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.layout = QHBoxLayout()
        
        first_text = QLabel(text)
        
        second_text = QLabel(text="  ")
        
        animation = QPropertyAnimation(second_text , b"pos")

        animation.setDuration(200)
        
        animation.setStartValue(QPoint(self.button.pos().x() + 110 , self.button.y() + 10))
        
        animation.setEndValue(QPoint(self.button.pos().y() + 130 , self.button.pos().x() + 10))
        
        leave_ani = QPropertyAnimation(second_text , b"pos")
        
        leave_ani.setDuration(200)
        
        leave_ani.setEndValue(QPoint(self.button.pos().x() + 110 , self.button.y() + 10))
        
        leave_ani.setStartValue(QPoint(self.button.pos().y() + 130 , self.button.pos().x() + 10))
        
        self.layout.addWidget(first_text)
        
        self.layout.addWidget(second_text)
        
        self.button.setLayout(self.layout)
        
        onhover = lambda x : animation.start()
        
        leave = lambda x: leave_ani.start()
        
        self.button.enterEvent = onhover
        
        self.button.leaveEvent = leave
        
        return self.button

class Animation:
    def movingAnimation(self , widget , endValue , duration):
        animation = QPropertyAnimation(widget , b"pos")
        
        animation.setStartValue(widget.pos())
        
        animation.setEndValue(endValue)
        
        animation.setDuration(duration)
        
        return animation
    
    def fadingAnimation(self , widget: QWidget , duration, reverse=False , startValue = 0, endValue = 0):
        # opacity = widget.graphicsEffect()
                
        # # if(opacity == None):
        opacity = QGraphicsOpacityEffect()
                 
        widget.setGraphicsEffect(opacity)
        
        animation = QPropertyAnimation(opacity , b"opacity")
        
        if(not reverse):
            animation.setStartValue(1)
            
            animation.setEndValue(endValue)
        else:
            animation.setStartValue(startValue)
        
            animation.setEndValue(1)
        
        animation.setDuration(duration)
        
        return animation

class QLayoutMaker:
    def __init__(self , icons: list[list[str]] , functions: list) -> None:
        self.icons = icons
        self.functions = functions
        
    def make(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        i = 0
        
        try:
            for icon, icon_color, icon_font_size, icon_family in self.icons:
                item = QCustomButton(icon, None).create()
                
                item.setStyleSheet(
                    "color: {}; font-size: {}px; font-family: {}".format(
                        icon_color, icon_font_size, icon_family
                    )
                )

                item.clicked.connect(self.functions[i])

                i += 1

                layout.addWidget(item)
        except:
            pass
        
        return layout

class QSliderMenu(QLabel):
    def __init__(self , parent) -> None:
        super().__init__(parent)
        
        self.head = parent
        
        self.setProperty("class" , "need")
        
        self.setGeometry(QRect(2000, 0, 400, 1000))

        self.show()

        layout = QVBoxLayout(self)

        self.scrollArea = QScrollArea(self)

        layout.addWidget(self.scrollArea)

        self.buttons = QWidget(self)

        self.buttons.setGeometry(QRect(100, 0, 400, 50))

        self.scrollArea.setWidget(self.buttons)

        self.second_layout = QVBoxLayout(self.buttons)

        self.buttons.setLayout(self.second_layout)
        
        self.setStyleSheet("""QLabel[class="need"] { border: 3px solid #3B4252 }""")

        
    def addMenu(self , name , widget , addAsLayout = False):
        childLayout = QVBoxLayout()
        
        if(name != ""):
            nameLabel = QLabel()
            
            nameLabel.setText(name)
            
            nameLabel.setFixedHeight(80)
            
            nameLabel.setStyleSheet("color: white; font-size: 20px; font-family: Comfortaa")
        
            childLayout.addWidget(nameLabel)
        
        if(addAsLayout):
            childLayout.addLayout(widget)
        else:
            childLayout.addWidget(widget)
        
        widget.setGeometry(self.geometry())
        
        self.second_layout.addLayout(childLayout)
        
        self.buttons.setFixedHeight(self.buttons.height() + 135)
