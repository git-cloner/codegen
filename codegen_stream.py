import requests
import time
from aiohttp import web
import json
from jaxformer.hf.sample import load_model, sampling
from gpt_j import gpt_load_model, gpt_generate_stream
from ChatGLM_6b import getAnswerFromChatGLM6b, getAnswerFromChatGLM6b_v2
from Vicuna_7b import getAnswerFromVicuna7b, getAnswerFromVicuna7b_v2

filter_string = None


def sampling_gptj(context, maxlength):
    gpt_load_model()
    return gpt_generate_stream(context, maxlength)


def filter_context(context):
    global filter_string
    if filter_string is None:
        print("loading filter")
        try:
            with open('filter.txt', mode='r', encoding='utf-8') as f:
                text = f.read().rstrip()
            filter_string = text.split('\n')
        except FileNotFoundError as err:
            filter_string = []
    for line in filter_string:
        if line in context:
            return True
    return False


async def codegen_stream(request):
    params = await request.json()
    context = params["context"]
    maxlength = params["maxlength"]
    modelname = params["modelname"]
    # filter
    if filter_context(context):
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"result_en": "请更换问题重新输入", "result_ch": "请更换问题重新输入",
                    "time": 0, "stop": True}
            ),
        )

    start = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "context : " + context)
    context = context.strip()
    f = lambda x='ddd': sum(
        [1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    flag_chs = f(context)
    stop = False
    if flag_chs:
        if modelname == 'vicuna-7b':
            result_en = getAnswerFromVicuna7b(context)
        else:
            result_en = getAnswerFromChatGLM6b(context)
        stop = result_en.endswith("[stop]")
        result_ch = result_en.replace("[stop]", "")
        if result_ch == "":
            result_ch = "思考中"
        result_en = result_ch
    else:
        result_en, stop = sampling(context, maxlength)
        result_ch = result_en
    end = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "result  : " + result_ch)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"result_en": result_en, "result_ch": result_ch,
                "time": end-start, "stop": stop}
        ),
    )


async def codegen_stream_v2(request):
    params = await request.json()
    context = params["context"]
    modelname = params["modelname"]
    prompt = context["prompt"]
    # filter
    if filter_context(prompt):
        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"response": "请更换问题重新输入",
                 "history": [],
                 "status": 403,
                 "time": 0,
                 "stop": True}
            ),
        )

    start = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "request : " + prompt)
    stop = False
    if modelname == 'vicuna-7b':
        result = getAnswerFromVicuna7b_v2(prompt)
    else:
        result = getAnswerFromChatGLM6b_v2(context)
    stop = result["response"] .endswith("[stop]")
    if result["response"] == "":
        result["response"] = "思考中"
    if stop:
        result["response"] = result["response"].replace("[stop]", "")
    end = time.perf_counter()
    result["time"] = end-start
    result["stop"] = stop
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "result  : " + result["response"])
    return web.Response(
        content_type="application/json",
        text=json.dumps(result),
    )
