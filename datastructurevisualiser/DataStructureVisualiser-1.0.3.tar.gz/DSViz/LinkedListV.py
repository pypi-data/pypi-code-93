from DSViz.NoneError import NoneError
import tkinter as tk
from tkinter.constants import BOTTOM, HORIZONTAL, RAISED
from PIL import ImageTk, Image  
from importlib import resources
import io

class LinkedListV:
    list = []

    def __init__(self, DLL = False, CLL = False):
        self.DLL = DLL
        self.CLL = CLL

    def addNode(self, node, head = False, tail = False):
        if node is None:
            raise NoneError('Node in Linked List cannot be None')

        if not isinstance(node, (str, float, int)):
            raise TypeError("Node in Linked List has to be of type String, Integer or Float")
        
        self.list.append(node)

    @property
    def show(self):

        if not isinstance(self.DLL, bool):
            if self.DLL is None:
                raise NoneError('DLL parameter cannot be None')
            raise TypeError('DLL parameter has to be True or False')
        
        if not isinstance(self.CLL, bool):
            if self.CLL is None:
                raise NoneError('CLL parameter cannot be None')
            raise TypeError('CLL parameter has to be True or False')

        window = tk.Tk()
        window.geometry("1000x800")
        window.title("Linked List Visualiser")

        main_frame = tk.Frame(window)
        main_frame.pack(fill=tk.BOTH, expand= True, side=tk.TOP)

        label = tk.Label(master = main_frame, text="Linked List looks like this: ")
        label.pack(side=tk.TOP)

        canvas = tk.Canvas(master=main_frame, width = 800, height = 600)
        canvas.pack( fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(master = main_frame, orient=HORIZONTAL, command=canvas.xview)
        scrollbar.pack(side = BOTTOM, fill=tk.X)
        canvas.configure(xscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        secondFrame = tk.Frame(canvas)
        canvas.create_window((0,0), window = secondFrame, anchor="nw")

        #select correct arrow
        if not self.DLL:
            with resources.open_binary('DSViz','arrow.png') as fp:
                arrowImage = fp.read()
            arrowImage = Image.open(io.BytesIO(arrowImage))
        else:
            with resources.open_binary('DSViz','doubleArrow.png') as fp:
                arrowImage = fp.read()
            arrowImage = Image.open(io.BytesIO(arrowImage))
        arrowImage = arrowImage.resize((50,50))

        tailIndex = 0
        for i in range(len(self.list)):
            subframe = tk.Frame(
                        master=secondFrame,
                        relief=tk.RAISED,
                        borderwidth=5
                    )
            subframe.grid(row=1, column=i, sticky='nsew')
            sub_subframe1 = tk.Frame(
                master=subframe,
                relief=tk.FLAT,
                borderwidth=5
            )
            sub_subframe1.grid(row=1, column=1, sticky='nsew')
            label = tk.Label(master=sub_subframe1, text = str(self.list[i]))
            label.pack(fill=tk.BOTH)

            sub_subframe2 = tk.Frame(
                master=subframe,
                relief=tk.FLAT,
                borderwidth=1
            )
            sub_subframe2.grid(row=1, column=2, sticky='nsew')
            
            itest = ImageTk.PhotoImage(arrowImage)
            arrow = tk.Label(master=sub_subframe2, image=itest)
            arrow.image=itest
            arrow.pack(fill=tk.BOTH)
        
        # pointer at the end of the list

        subframe = tk.Frame(
                        master=secondFrame,
                        relief=tk.RAISED,
                        borderwidth=5
                    )
        subframe.grid(row=1, column=len(self.list), sticky='nsew')

        if self.CLL:
            label = tk.Label(master = subframe, text = "Head")
        else:
            label = tk.Label(master = subframe, text = "Null")
        label.pack(fill=tk.BOTH)        
        window.mainloop()
            