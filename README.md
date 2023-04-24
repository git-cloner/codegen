# Codegen

Salesforce codegen,THUDM/ChatGLM-6B with web server

Fork from https://github.com/salesforce/CodeGen

Add web server support 

Support THUDM/ChatGLM-6B Now

## Online demo

https://gitclone.com/aiit/chat/

## Visual Studio Code  Extension

https://github.com/git-cloner/codegeeker

 ![](https://gitclone.com/download1/aiit/codegeeker.gif)

 ![](https://gitclone.com/download1/aiit/gpt-2.gif)

## reference
https://zhuanlan.zhihu.com/p/598982945 做一个生产级别的类似ChatGPT的聊天机器人<br>
https://www.zhihu.com/zvideo/1596160335995641856 基于gpt-j-6b的聊天机器人<br>
https://zhuanlan.zhihu.com/p/594946225 在亚马逊aws的云主机上搭建gpt-j-6b模型<br>
https://zhuanlan.zhihu.com/p/588616069 做一个类似github copilot的免费代码生成器<br>
https://zhuanlan.zhihu.com/p/620233511 清华ChatGLM-6B模型实践<br>
https://zhuanlan.zhihu.com/p/620070973 ColossalAI推理实践<br>
https://zhuanlan.zhihu.com/p/619954588 Chinese-LLaMA-Alpaca实践<br>
https://zhuanlan.zhihu.com/p/624286959 FastChat部署与流式调用实践

## usage

### Clone code

git clone https://gitclone.com/github.com/git-cloner/codegen

### Install

#### 1.install Nvidia Graphics Card and Driver

#### 2.install conda

#### 3.init vitual runtime

```shell
conda create -n codegen python=3.8
conda activate codegen
pip install pillow -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install torch torchvision torchaudio -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install transformers==4.25.1 -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install accelerate -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install aiohttp==3.8.3 -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install aiohttp_cors==0.7.0 -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
#pip install huggingface for gpt-neo
pip install datasets -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install gradio -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
pip install sentencepiece==0.1.91 -i http://pypi.douban.com/simple --trusted-host=pypi.douban.com
```

### Download model

```shell
wget -P checkpoints https://storage.googleapis.com/sfr-codegen-research/checkpoints/codegen-350M-nl.tar.gz && tar -xvf checkpoints/codegen-350M-nl.tar.gz -C checkpoints/
wget -P checkpoints https://storage.googleapis.com/sfr-codegen-research/checkpoints/codegen-350M-multi.tar.gz && tar -xvf checkpoints/codegen-350M-multi.tar.gz -C checkpoints/
wget -P checkpoints https://storage.googleapis.com/sfr-codegen-research/checkpoints/codegen-350M-mono.tar.gz && tar -xvf checkpoints/codegen-350M-mono.tar.gz -C checkpoints/
```

### run as web server
```shell
conda activate codegen
python codegen.py
```

### test
post: http://127.0.0.1:5000/codegen or direct post to :https://gitclone.com/aiit/codegen

#### Use Salesforce codegen

input params: {"context":"def hello_world():","maxlength":128}

return params: 
{
    "result": "\n        print(\"Hello world\")\n        hello_world()\n      ",
    "time": 1.9620850095525384
}

#### Use THUDM/ChatGLM-6B

input params: {"context":"写一个python版的数组排序","maxlength":128}
