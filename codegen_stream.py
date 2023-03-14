import requests
import time
from aiohttp import web
import json
from jaxformer.hf.sample import load_model, sampling
from gpt_j import gpt_load_model, gpt_generate_stream


def sampling_gptj(context, maxlength):
    gpt_load_model()
    return gpt_generate_stream(context, maxlength)


async def codegen_stream(request):
    params = await request.json()
    context = params["context"]
    maxlength = params["maxlength"]
    modelname = params["modelname"]
    start = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "context : " + context)
    context = context.strip()
    f = lambda x='ddd': sum(
        [1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    flag_chs = f(context)
    stop = False
    if flag_chs:
        results = sampling_gptj(context, maxlength)
        results = json.loads(results)
        result_en = results["result_en"]
        result_ch = results["result_ch"]
    else:
        result_en,stop = sampling(context, maxlength)
        result_ch = result_en
    end = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",
          time.localtime()), "result  : " + result_ch)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"result_en": result_en, "result_ch": result_ch, "time": end-start,"stop":stop}
        ),
    )
