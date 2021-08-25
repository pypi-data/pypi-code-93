class button_box(object):
    def __init__(self,title="button_box",text="",value=["按钮"]):
        import tkinter
        import sys
        root=tkinter.Tk()
        root.geometry("400x300")
        root.title(title)
        label=tkinter.Label(root,text=text)
        label.pack()
        for i in value:
            def var():
                self.box=i
                root.quit()
            button=tkinter.Button(root,text=i,command=var)
            button.pack()
        root.mainloop()
class input_box(object):
    def __init__(self,title="input_box",text=""):
        import tkinter
        import sys
        global box
        root=tkinter.Tk()
        root.geometry("400x300")
        root.title(title)
        label = tkinter.Label(root, text=text)
        label.pack()
        entry=tkinter.Entry(root)
        entry.pack()
        def var():
            self.box=entry.get()
            root.quit()
        button=tkinter.Button(root,text="确定",command=var)
        button.pack()
        root.mainloop()
class choice_box(object):
    def __init__(self,title="choice_box",text="",value=["按钮"]):
        import tkinter
        import sys
        root=tkinter.Tk()
        root.geometry("400x300")
        root.title(title)
        label=tkinter.Label(root,text=text)
        label.pack()
        lb=tkinter.Listbox(root)
        for i in range(len(value)):
            lb.insert(i,value[i])
        lb.pack()
        def var():
            self.box=lb.get(0)
            root.quit()
        button=tkinter.Button(root,text="确定",command=var)
        button.pack()
        root.mainloop()