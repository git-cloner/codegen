import asyncio
import json
import time
import os
import aiohttp_cors
import requests
from functools import lru_cache
from aiohttp import web
from jaxformer.hf.sample import load_model,sampling
from gpt_j import gpt_load_model,gpt_generate
from codegen_stream import codegen_stream

ROOT = os.path.dirname(__file__)

async def index(request):
    content = open(os.path.join(ROOT, "index.html"),
                   "r", encoding='utf-8').read()
    print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),"index : " + request.remote)
    return web.Response(content_type="text/html", text=content)

@lru_cache(maxsize=1024, typed=False)
def getAnswerFromChatGPTJ(context,maxlength):
    gpt_load_model()
    return gpt_generate(context,maxlength)

async def codegen(request):
    params = await request.json()
    context = params["context"]
    maxlength = params["maxlength"]
    #support chs
    flag_chs = False
    f = lambda x='ddd':sum([1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x])>0
    flag_chs = f(context)
    if ( flag_chs and context.strip().endswith(":")):
        context = context.strip()[0:-1]
    #support !
    if not flag_chs:
        flag_chs = context.strip().endswith("!")
        if flag_chs:
           context = context.strip()[0:-1] 
    start = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),"context : " + context)
    context = context.replace("//","").replace("#","").strip()
    stop = False
    if flag_chs :#or content.startwith('gpt-j') :
        result = getAnswerFromChatGPTJ(context,maxlength).replace(context,"")
    else:
        result,stop = sampling(context,maxlength)
    end = time.perf_counter()
    print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),"result  : " + result)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"result": result,"time":end-start,"stop":stop}
        ),
    )

app = web.Application()
cors = aiohttp_cors.setup(app)
app.router.add_get("/", index)
app.router.add_get("/codegen", index)
app.router.add_post("/codegen", codegen)
app.router.add_post("/codegen_stream", codegen_stream)

for route in list(app.router.routes()):
    cors.add(route, {
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })

if __name__ == "__main__":
    load_model()
    print("Start web server") 
    web.run_app(
        app, access_log=None, host="0.0.0.0", port=5000, ssl_context=None
    )
