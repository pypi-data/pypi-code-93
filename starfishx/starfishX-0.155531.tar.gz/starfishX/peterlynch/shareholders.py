import starfishX as sx

keywordList = ["นาย","นาง","พญ","พ.ญ.","น.ส.","ท่านผู้หญิง","ร.ต.","mr","mrs","miss","เด็กชาย","ด.ช.",
                   "เด็กหญิง","ด.ญ.","พ.อ.","พ.ท.","พ.ต.","ร้อยตรี","ร้อยโท","ร้อยเอก","เรือตรี","เรือโท","เรือเอก"
                   "เรืออากาศเอก","พันเอก","พันโท","แพทย์","หม่อม","ม.ล.","ม.ร.ว","พลตำรวจ","พันตำรวจ","ร.ท."
                   "ว่าที่","ร.ศ.","ดร.","คุณหญิง","รองศาสตราจารย์","นพ.","น.พ.","สมเด็จพระ",]
def filterPerson(n):    
    for i in keywordList:  
     if(i in n.lower()):
        return False
    return True

def filterPersonC(n):    
    for i in keywordList:  
     if(i in n.lower()):
        return True
    return False

def filter2float(n):
    n = n.str.replace(',', '')
    n = n.astype(float)  
    return n

def getRatioPersonalShareholders(symbol):
    logAll = sx.listShareholders(symbol)
    logAll['Share'] = filter2float(logAll['Share'])

    logIn = logAll[logAll["Name"].map(filterPerson)] 
    logPerson = logAll[logAll["Name"].map(filterPersonC)] 

    inHold = logIn["Share"].sum()
    allHold = logAll["Share"].sum()
    r = inHold/allHold
    return (r),logIn,logPerson,logAll


