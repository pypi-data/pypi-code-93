import time
import requests

response = requests.get('http://35.225.89.124/push_commit')
res=response.content
print(res)
res=str(res)
index=res.index("'")
index1=res.index("'",index+1)
res=res[index+1:index1]
print(res)