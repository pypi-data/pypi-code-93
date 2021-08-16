from TeraApp1.TeraApp.AppScreen.AppScreen import *
app = TeraApp('TeraApp', 500, 500, 'darkslategray') #500 = x,500(2) = y
app.txtc('Titledddddddddddddddddddddddd', 240,70, 15, 'blue') #(x = 240), (y = 2), (15 = txt size)
input1 = app.input(210, 80, 'white')

def fds():
    print(app.input_name.text())


app.buttonf('save', 210,100, 'green', fds)
app.app.exec()

