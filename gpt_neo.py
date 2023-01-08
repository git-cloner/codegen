from functools import lru_cache
from transformers import pipeline
import gradio as gr
import torch
import requests

#generator = None
translator_zh2en = None
translator_en2zh = None


def gpt_load_model():
    #global generator
    global translator_zh2en
    global translator_en2zh
    #if generator is None:
    #    #torch.cuda.set_device('cuda:1')
    #    generator = pipeline(
    #        'text-generation', model='EleutherAI/gpt-neo-1.3B')
    if translator_zh2en is None:
        translator_zh2en = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-zh-en")
    if translator_en2zh is None:
        translator_en2zh = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-en-zh")

def getAnswerFromChatGPTJ6B(context):
    url = 'http://127.0.0.1:8081/generate/'
    data = '{' + '"text": "' + context + '",' + '"generate_tokens_limit": 64,'+ '"top_p": 0.7,'+'"top_k": 0,' + '"temperature":0.9' +'}' ;
    headers = {'content-type': 'application/json;charset=utf-8'}
    r = requests.post(url,data= data.encode(), headers=headers)
    res = r.json()
    return res['completion']

@lru_cache(maxsize=1024, typed=False)
def gpt_generate(inputs, maxlength):
    #global generator
    global translator_zh2en
    global translator_en2zh
    f = lambda x='ddd': sum(
        [1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    print("inputs: ", inputs)
    flag_chs = f(inputs)
    if flag_chs:
        inputs = translator_zh2en(inputs)[0]['translation_text']
        print("zh2en: ", inputs)
    #results = generator(inputs, max_length=int(maxlength),
    #                    do_sample=True, temperature=0.9)
    results = getAnswerFromChatGPTJ6B(inputs)
    print("output: ", results)
    if flag_chs:
        #results = translator_en2zh(results[0]['generated_text'])
        results = translator_en2zh(results)
        print("en2zh:", results)
        return results[0]['translation_text']
    else:
        return results

def chat(message, history):
    history = history or []
    response = gpt_generate(message,128)
    history.append((message, response))
    return history, history

def create_ui():
    chatbot = gr.Chatbot().style(color_map=("green", "gray"))
    interface = gr.Interface(
        chat,
        ["text", "state"],
        [chatbot, "state"],
        allow_flagging="never",
    )
    interface.launch(server_name='0.0.0.0')

if __name__ == "__main__":
    torch.cuda.set_device(1)
    print("torch gpu: ", torch.cuda.is_available())
    gpt_load_model()
    print("load model")
    create_ui()
