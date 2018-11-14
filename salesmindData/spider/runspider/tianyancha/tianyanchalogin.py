
import json
from hashlib import md5
import requests
temp = md5()
temp.update('jackie1102'.encode('utf-8'))
code = temp.hexdigest()
data = json.dumps({"mobile":"17610273593","cdpassword":code,"loginway":"PL",'autoLogin': True})
r = requests.post('https://www.tianyancha.com/cd/login.json',data=data,headers={'Content-Type': 'application/json; charset=UTF-8'})
data = json.loads(r.text)
print(data)
value = data['data']['token']
print(value)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Cookie': 'auth_token='+ value
}
r = requests.get('https://www.tianyancha.com',headers=headers)
print(r.text)





