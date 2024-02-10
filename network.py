import urllib.request
import urllib.parse
import json

#url = "https://api.example.com/get_data"
host = "https://"
endpoint = "purchaceStatus"
url = f"{host}/{endpoint}"
params = {'param1': 'value1', 'param2': 'value2'}
headers = {'Authorization': 'Bearer my_token'}

data = urllib.parse.urlencode(params).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers)

with urllib.request.urlopen(req) as res:
    body = res.read().decode('utf-8')
    if res.status == 200:
        data = json.loads(body)
        # データを加工するなどの処理を行う
    else:
        print("Error: ", res.status)