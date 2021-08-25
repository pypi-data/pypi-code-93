from kivy.app import App
from kivy.core.text import markup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
import os
import time
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color

blue = (0.1, .85, 1, 1)


def filePath() -> str:
    return os.path.dirname(os.path.abspath(__file__))

class MyLabel(Label):
   def on_size(self, *args):
      self.text_size = self.size

"""
self.mainLogo = Button(size_hint=(None, None), size=(120,120))
with self.mainLogo.canvas:
    Image(source=f"{filePath()}/assets/mainIcon.png", size=self.mainLogo.size, pos=self.mainLogo.pos, allow_stretch=True, keep_ratio=False)
self.root.add_widget(self.mainLogo)
"""
"""Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '900')
Config.write()"""


class MainApp(App):
    def build(self):
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', '450')
        self.number = 1
        Window.size = (800, 450)
        #nommer la fenêtre
        self.title = "Petchou Launcher"
        
        #créer la vue principale
        layout = GridLayout(cols=6, rows=4, row_force_default= True, row_default_height= 240 , col_force_default= True, col_default_width = 250)
        
        
        #ajouter un label
        self.label = MyLabel(text="\n  Quelle application voulez-vous lancer ?", markup=True, halign="left", valign="top", font_size="35sp", width=1400, size_hint_x=None, color = blue)
        layout.add_widget(self.label)
        
        empty1 = Button(text="", 
                    background_color=[0,0,0,0])
        empty2 = Button(text="                  ", 
                    background_color=[0,0,0,0])
        empty3=  Button(text="", 
                    background_color=[0,0,0,0])
        empty4= Button(text="", 
                    background_color=[0,0,0,0])
        layout.add_widget(empty1)
        layout.add_widget(empty2)
        layout.add_widget(empty3)
        layout.add_widget(empty4)
        
        #ajouter une image
        self.logo = Button(text ="",
                     
                     background_normal = f"{filePath()}/assets/mainIcon.png",
                     background_down =f"{filePath()}/assets/mainIcon.png",
                     size_hint_x= None,
                     width=250
                     ) 
        self.logo.bind(on_press=self.logoPress)
        layout.add_widget(self.logo)

        #ajouter des boutons à grid
        morpion = Button(text =" ",
                     background_normal = f"{filePath()}/assets/morpionIcon.png",
                     background_down =f"{filePath()}/assets/morpionIcon.png",
                     size_hint_x= None,
                     width=250
                     ) 
        morpion.bind(on_press=self.morpionLaunch)
        layout.add_widget(morpion)

        #envoyer l'écran
        return layout

    def morpionLaunch(self, instance):
        App.get_running_app().stop()
        Window.close()
        os.system('bash -c "python3 -m Morpion"')



    def logoPress(self, instance):
        if self.number == 1:
            self.label.text = "Bien joué, je suis démasqué !"
            self.number = 0
        
        elif self.number == 0:
            self.label.text ="Quelle application voulez-vous lancer ?"
            self.number = 1


if __name__ == "__main__":
    app = MainApp()
    app.run()