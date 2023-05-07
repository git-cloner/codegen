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


def getAnswerFromVicuna7b_v2(contextx):
    url = 'http://172.16.62.137:8000/v1/chat/completions/stream'
    messages = []
    prompt = contextx["prompt"]
    for i in range(len(contextx["history"])):
        messages.append({"role": "user", "content": contextx["history"][i][0]})
        messages.append(
            {"role": "assistant", "content": contextx["history"][i][1]})
    messages.append({"role": "user", "content": prompt})
    data_json = {"model": "vicuna-7b-v1.1",
                 "messages": messages}
    data = json.dumps(data_json)
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url, data=data, headers=headers)
    res = r.json()
    history = []
    history_json = res["history"]
    his = None
    for h in history_json:
        if his is None:
            his = [h["content"]]
        elif len(his) == 1:
            his.append(h["content"])
            history.append(his)
            his = None
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if r.status_code == 200:
        return {'response': res['response'], 'history': history, 'status': 200, 'time': now}
    else:
        return {'response': '算力不足，请稍候再试！[stop]', 'history': [], 'status': 200, 'time': now}
