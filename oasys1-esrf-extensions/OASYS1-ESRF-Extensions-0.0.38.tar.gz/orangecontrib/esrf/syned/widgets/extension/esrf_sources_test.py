
url = 'ftp://ftp.esrf.eu/pub/scisoft/syned/lightsources/'
url2 = 'http://ftp.esrf.eu/pub/scisoft/syned/lightsources/'

from urllib.request import urlopen

urlpath = urlopen(url)
string0 = urlpath.read().decode('utf-8')
string = string0.split("\n")

mylist  = []
for line in string:
    list1 = line.strip().split(" ")
    filename = list1[-1]
    if "EBS" in filename:
        mylist.append(filename)

print(mylist)

filename = mylist[10]
print(">>>", filename)
remotefile = urlopen(url2 + filename)
localfile = open("tmp/" + filename,'wb')
localfile.write(remotefile.read())
localfile.close()
remotefile.close()

print(mylist)