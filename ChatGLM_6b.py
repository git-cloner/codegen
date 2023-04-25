import requests
import json

def getAnswerFromChatGLM6b(context):
    url = 'http://172.16.62.136:8000/stream'
    data=json.dumps(
            {"prompt": context, "history": []}
        )
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url, data=data, headers=headers)
    res = r.json()
    if r.status_code == 200:
        return res['response']
    else:
        return '算力不足，请稍候再试！[stop]'