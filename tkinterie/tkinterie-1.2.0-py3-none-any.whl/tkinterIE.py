#基于InternetExplorer.Application的tkinter webview组件
#事实上，该com组件依赖于系统的浏览器内核
#所以，以Windows10为例，内核是edge而非ie
from tkinter import Tk,Frame
from comtypes.client import CreateObject,GetEvents,PumpEvents
from ctypes import windll
SetParent=windll.user32.SetParent
MoveWindow=windll.user32.MoveWindow
GetWindowLong=windll.user32.GetWindowLongA
SetWindowLong=windll.user32.SetWindowLongA


class WebView(Frame):

    def __init__(self,parent,width:int,height:int,url='',**kw):
        Frame.__init__(self,parent,width=width,height=height,**kw)
        ie=CreateObject('InternetExplorer.Application')
        ie.AddressBar=False
        ie_id=ie.HWND
        frame_id=self.winfo_id()
        style=GetWindowLong(ie_id,-16)
        SetWindowLong(ie_id,-16,style&~12582912&~262144)
        SetParent(ie_id,frame_id)
        MoveWindow(ie_id,0,0,width,height,True)
        ie.Visible=True
        if url!='':
            ie.Navigate2(url)
        self.ie=ie
        self._go_bind()

    def _go_bind(self):
        self.bind('<Configure>',self.__resize_webview)
        self.bind('<Destroy>',self.__delete_ie)

    def __resize_webview(self,event):
        self.ie.Width=self.winfo_width()
        self.ie.Height=self.winfo_height()

    def __delete_ie(self,event):
        self.ie.Quit()
        del self.ie

    def navigate(self,url:str):
        self.ie.Navigate2(url)


if __name__=='__main__':
    a=Tk()
    a.geometry('1200x600')

    w=WebView(a,1200,550,'www.baidu.com')
    w.pack(side='bottom',fill='both')

    a.mainloop()
