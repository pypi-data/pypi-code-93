from os import path
from cryoloBM import helper_GUI
import matplotlib.pyplot as plt

from cryoloBM import MySketch # for type hinting purpose
from numpy import ndarray # for type hinting purpose
from typing import List,Tuple

class ChildDlg(helper_GUI.QtG.QDialog):
    is_visible = True
    def closeEvent(self, event:helper_GUI.plt_qtbackend)->None:
        self.is_visible = False

class PreviewWindow(helper_GUI.QtG.QMainWindow):
    def __init__(self, font:helper_GUI.QFont, list_patches:Tuple[MySketch.MySketch] = tuple(), title:str = "Preview")->None:
        super(PreviewWindow, self).__init__(None)

        self.title = title
        self.current_image_path = None
        self.current_pure_filename = None
        self.list_patches = list_patches
        self.index = None

        # SETUP QT
        self.font = font
        self.fig = None
        self.ax = None
        self.im = None
        self.plot = ChildDlg(self)
        self.img = None



    def set_current_image_paths(self, img_path:str)->None:
        """
        Set the img paths
        """
        self.current_image_path = img_path
        self.current_pure_filename = path.splitext(path.basename(self.current_image_path))[0]

    def set_list_patches(self,list_patches:List[MySketch.MySketch])->None:
        """
        Set the list_patches
        """
        if self.ax:
            self.ax.patches=[]      #delete all the patches that represent the patches on the last displayed slice
        self.list_patches = list_patches

    def display_img(self, img_path:str, img:ndarray, index:int, reload_img:bool = False)->None:
        """
        Set the variable to show an image. I copied some code from 'box_manager._set_first_time_img' function
        :param img_path: path of 'img' used to set the 'current_image_path' variable
        :param img: 2D numpy img
        :param index: slice index
        :param reload_img: If True we do not have to set self.img again
        :return: none
        """
        self.set_is_visible(True)
        if reload_img is False:
            if img is not None:
                #change image case
                self.img = img
            else:
                #boxmanager.onclick case
                img=self.img

        self.set_current_image_paths(img_path)
        self.index = index

        # Display the image
        if self.im is None:
            self.fig, self.ax = plt.subplots(1)
            self.ax.xaxis.set_visible(False)
            self.ax.yaxis.set_visible(False)
            self.fig.tight_layout()
            self.im = self.ax.imshow(img, origin="lower", cmap="gray", interpolation="Hanning")
            # The following variables have to set only once otherwise even if you change img it will not be displayed
            self.fig.canvas.draw()
            self.plot.canvas = helper_GUI.plt_qtbackend.FigureCanvasQTAgg(self.fig)
            layout = helper_GUI.QtG.QVBoxLayout()
            layout.addWidget(self.plot.canvas)
            self.plot.setLayout(layout)
        else:
            self.im.set_data(img)

        for b in self.list_patches:
            self.ax.add_patch(b)        # it clip the box on the fig image and not on the window

        self.plot.canvas.draw()
        self.plot.setWindowTitle(self.title+": "+self.current_pure_filename + " index: " + str(index))

        # move the pop up window, it avoids to overlap the boxmanager window
        resolution = helper_GUI.QtG.QDesktopWidget().screenGeometry()
        self.move(
            (resolution.width() / 2) + (self.frameSize().width()),
            (resolution.height() / 2) + (self.frameSize().height()),
            )

        self.plot.show()


    def reload_img(self)->None:
        self.display_img(self.current_image_path,self.img,self.index, True)

    def is_visible(self)->bool:
        return self.plot and self.plot.is_visible

    def set_is_visible(self,is_visible)->None:
        if self.plot:
            self.plot.is_visible = is_visible