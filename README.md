# Codegen

Salesforce codegen with web server

Fork from https://github.com/salesforce/CodeGen

Add web server support 

## Online demo

https://gitclone.com/aiit/codegen

## Visual Studio Code  Extension

https://github.com/git-cloner/codegeeker

 ![](https://gitclone.com/download1/aiit/codegeeker.gif)

 ![](https://gitclone.com/download1/aiit/codegen.gif)

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
pip install pillow
pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers==4.16.2
pip install aiohttp==3.8.3
pip install aiohttp_cors==0.7.0
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
input params: {"context":"def hello_world():","maxlength":128}

! note: maxlength is an integral multiple of 32

return params: 
{
    "result": "\n        print(\"Hello world\")\n        hello_world()\n      ",
    "time": 1.9620850095525384
}
