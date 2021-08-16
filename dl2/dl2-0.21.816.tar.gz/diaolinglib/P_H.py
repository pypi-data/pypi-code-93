from pyecharts.charts import*
#条形图
def _bar(x,y,n,n2):
    dexbname=Bar()
    dexbname.add_xaxis(x)
    dexbname.add_yaxis(n,y)
    dexbname.render("{}.html".format(n2))
#线形图
def _line(x,y,n,n2):
    dexlname=Line()
    dexlname.add_xaxis(x)
    dexlname.add_yaxis(n,y)
    dexlname.render("{}.html".format(n2))
