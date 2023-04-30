import requests
import json
import datetime


def getAnswerFromVicuna7b(context):
    url = 'http://172.16.62.137:8000/v1/chat/completions/stream'
    data = json.dumps(
        {"model": "vicuna-7b-v1.1",
            "messages": [{"role": "user", "content": context}]}
    )
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url, data=data, headers=headers)
    res = r.json()
    if r.status_code == 200:
        return res['response']
    else:
        return '算力不足，请稍候再试！[stop]'


def getAnswerFromVicuna7b_v2(context):
    url = 'http://172.16.62.137:8000/v1/chat/completions/stream'
    data = json.dumps(
        {"model": "vicuna-7b-v1.1",
            "messages": [{"role": "user", "content": context}]}
    )
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url, data=data, headers=headers)
    res = r.json()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if r.status_code == 200:
        return {'response': res['response'], 'history': [], 'status': 200, 'time': now}
    else:
        return {'response': '算力不足，请稍候再试！[stop]', 'history': [], 'status': 200, 'time': now}
