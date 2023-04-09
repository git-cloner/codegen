import requests
import json
import os

def getAnswerFromChatGLM6b(context):
    if os.name == 'nt':
        url = 'http://172.16.62.66:8000/stream'
    else:
        url = 'http://172.16.62.136:8000/stream'
    data = '{"prompt": "'  + context +  '", "history": []}'
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url, data=data.encode(), headers=headers)
    res = r.json()
    if r.status_code == 200 :
        return res['response']
    else:
        return ""