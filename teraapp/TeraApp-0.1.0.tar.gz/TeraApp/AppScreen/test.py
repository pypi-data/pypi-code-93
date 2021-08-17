from TeraApp1.TeraApp.AppScreen.AppScreen import *
app = TeraApp('TeraApp', 700, 700, 'darkslategray') #500 = x,500(2) = y
app.inputr(210, 300, 'blue', 100, 100)
app.appbar('red',100)
app.txtc('Titledddddddddddddddddddddddd', 240,40, 15, 'blue') #(x = 240), (y = 2), (15 = txt size)


def fds():
    print(app.input_name.text())


app.buttonf('save', 210,50, 'green', fds)
app.app.exec()

