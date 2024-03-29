import urllib.request
import urllib.parse
import json

# 本番用URL
host = "https://roboconwebapps.azurewebsites.net"
endpoint = "purchase_status"

"""
# デバッグ用URL
host = "https://api.github.com"
endpoint =  "users/switch23"
"""

# URL作成
url = f"{host}/{endpoint}"


# フラグ取得メソッド
def get_flag():
    req = urllib.request.Request(url)

    # パラメータとデータの設定
    """
    params = {'param1': 'value1', 'param2': 'value2'}
    headers = {'Authorization': 'Bearer my_token'}
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    """

    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
        if res.status == 200:
            data = json.loads(body)
            print(data)
            # 取得結果を返却
            return data['purchase_flag']
        else:
            print("Error: ", res.status)
            return False
