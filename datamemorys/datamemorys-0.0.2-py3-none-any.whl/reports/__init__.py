from datamemorys.datas import SYCMDataFrame
from LAC import LAC
from pandas import DataFrame
def getKeyWordsReports(loginAccName,cateid='0',device='0',priceSeg='-1',dateType='month'):
    loginAccName=loginAccName.split(":")[0]
    df=SYCMDataFrame("items_hotsearch",loginAccName)
    if cateid!='0' or cateid!=0:
        df=df[df['类目id']==str(cateid)]
    if device!='0' or device!=0:
        df=df[df['设备类型']==str(device)]
    if priceSeg!='-1' or priceSeg!=-1:
        df=df[df['价格带']==str(priceSeg)]
    if dateType!='month' :
        df=df[df['日期类型']==str(dateType)]
    lac=LAC(mode='seg')
    df['date_']=df['日期'].apply(lambda x:x.split("|")[0].split("%7C")[0])
    res=DataFrame()
    for t,itemid,d,seIpvUv,sales,uv in df[['商品名','商品id','date_','转换后搜索的Ipv人数','转换后交易额','转换后访客数']].values:
        ws=lac.run(t)
        ws=list(set(ws))        
        tdf=DataFrame({'words':ws})
        tdf['date']=d
        tdf['seIpvUv']=seIpvUv
        tdf['sales']=sales
        tdf['uv']=uv
        tdf['itemid']=itemid
        tdf['title']=t
        res=res.append(tdf) 
    return res