import requests
import json
def get_api(http,*w):
	s = requests.Session()
	header = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate',
			  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
			  'Cookie': 'xesId=b524835904a4a420cba3dde34890bade; user-select=scratch;  xes_run_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIuY29kZS54dWVlcnNpLmNvbSIsImF1ZCI6Ii5jb2RlLnh1ZWVyc2kuY29tIiwiaWF0IjoxNjAxODA5NDcxLCJuYmYiOjE2MDE4MDk0NzEsImV4cCI6MTYwMTgyMzg3MSwidXNlcl9pZCI6bnVsbCwidWEiOiJNb3ppbGxhXC81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXRcLzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZVwvODUuMC40MTgzLjEyMSBTYWZhcmlcLzUzNy4zNiBFZGdcLzg1LjAuNTY0LjY4IiwiaXAiOiIxMTIuNDkuNzIuMTc1In0.9bXcb813GhSPhoUJkezZpV8O50ynm0hhYvszNyczznQ; prelogid=ef8f6d12febabf75bf9599744b73c6f5; xes-code-id=87f66376f1afd34f70339baeca61b7a1.8dbd833da9122d69a17f91054066dbb3; X-Request-Id=82f1c3968c8ff01ee151a0413f56aa84; Hm_lpvt_a8a78faf5b3e92f32fe42a94751a74f1=1601809487',
			  'Host': 'code.xueersi.com', 'Proxy-Connection': 'keep-alive',
			  'Referer': 'http://code.xueersi.com/space/11909587',
			  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.68'}
	total = json.loads(_nice(s.get(http, headers=header).text))
	return total
def get_data():
    import time
    head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"}
    a=getCookies()
    num=a.index("stu_id=")+7
    id=""
    for i in range(num,num+100):
        if a[i]!=";":
            id=id+a[i]
        else:
           break
    cwx=requests.get("https://code.xueersi.com/api/space/profile?user_id={}".format(id),headers=head)
    cwx.encoding = "UTF-8"
    soup=bs4.BeautifulSoup(cwx.text,"lxml")
    d=soup.find(name="p").text
    _dic={}
    _dic["你的id"]=id
    _dic["你的粉丝量"]=d[d.find("fans")+6:d.find("follows")-2]
    _dic["你的关注量"]=d[d.find("follows")+9:d.find("disabled")-2]
    _dic["你的姓名"]=get_api("https://code.xueersi.com/api/space/profile?user_id="+id)["data"]["realname"]
    _dic["你的个性签名"]=get_api("https://code.xueersi.com/api/space/profile?user_id="+id)["data"]["signature"]
    return _dic