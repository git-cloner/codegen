import asyncio
import json
import time
import aiohttp_cors
from aiohttp import web
from jaxformer.hf.sample import load_model,sampling

async def index(request):
    content = '<h1>code gen</h1>'
    return web.Response(content_type="text/html", text=content)

async def codegen(request):
    params = await request.json()
    context = params["context"]
    maxlength = params["maxlength"]
    start = time.perf_counter()
    result = sampling(context,maxlength)
    end = time.perf_counter()
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"result": result,"time":end-start}
        ),
    )

app = web.Application()
cors = aiohttp_cors.setup(app)
app.router.add_get("/", index)
app.router.add_post("/codegen", codegen)

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
