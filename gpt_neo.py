from transformers import pipeline
import gradio as gr
import torch

generator = None
translator_zh2en = None
translator_en2zh = None


def gpt_load_model():
    global generator
    global translator_zh2en
    global translator_en2zh
    if generator is None:
        torch.cuda.set_device(1)
        generator = pipeline(
            'text-generation', model='EleutherAI/gpt-neo-1.3B')
    if translator_zh2en is None:
        translator_zh2en = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-zh-en")
    if translator_en2zh is None:
        translator_en2zh = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-en-zh")


def gpt_generate(inputs, maxlength):
    global generator
    global translator_zh2en
    global translator_en2zh
    f = lambda x='ddd': sum(
        [1 if u'\u4e00' <= i <= u'\u9fff' else 0 for i in x]) > 0
    print("inputs: ", inputs)
    flag_chs = f(inputs)
    if flag_chs:
        inputs = translator_zh2en(inputs)[0]['translation_text']
        print("zh2en: ", inputs)
    results = generator(inputs, max_length=int(maxlength),
                        do_sample=True, temperature=0.9)
    print("output: ", results)
    if flag_chs:
        results = translator_en2zh(results[0]['generated_text'])
        print("en2zh:", results)
        return results[0]['translation_text']
    else:
        return results[0]['generated_text']


def create_ui():
    inputs = gr.inputs.Textbox(lines=10, placeholder="Enter sentence...")
    maxlength = gr.Dropdown(choices=["64", "128", "256", "1024"], value="64")
    interface = gr.Interface(fn=gpt_generate,
                             inputs=[inputs, maxlength],
                             outputs=gr.outputs.HTML(label="output"),
                             title='gpt-neo generator')
    interface.launch(server_name='0.0.0.0')


if __name__ == "__main__":
    torch.cuda.set_device(1)
    print("torch gpu: ", torch.cuda.is_available())
    gpt_load_model()
    print("load model")
    create_ui()
