# Copyright (c) 2022, salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import os
import re
import time
import random
import argparse
from functools import lru_cache

import torch

from transformers import GPT2TokenizerFast
from jaxformer.hf.codegen.modeling_codegen import CodeGenForCausalLM

g_device = None
g_model = None
g_tokenizer = None
g_pad_token_id = None
g_batch_size = None
g_temp = None
g_top_p = None


########################################################################
# util


class print_time:
    def __init__(self, desc):
        self.desc = desc

    def __enter__(self):
        print(self.desc)
        self.t = time.time()

    def __exit__(self, type, value, traceback):
        print(f'{self.desc} took {time.time()-self.t:.02f}s')


def set_env():
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'


def set_seed(seed, deterministic=True):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.backends.cudnn.deterministic = deterministic
        torch.backends.cudnn.benchmark = not deterministic
        # torch.use_deterministic_algorithms(deterministic)


def cast(model, fp16=True):
    if fp16:
        model.half()
    return model


########################################################################
# model


def create_model(ckpt, fp16=True):
    if fp16:
        return CodeGenForCausalLM.from_pretrained(ckpt, revision='float16', torch_dtype=torch.float16, low_cpu_mem_usage=True)
    else:
        return CodeGenForCausalLM.from_pretrained(ckpt)


def create_tokenizer():
    t = GPT2TokenizerFast.from_pretrained('gpt2')
    t.max_model_input_sizes['gpt2'] = 1e20
    return t


def include_whitespace(t, n_min=2, n_max=20, as_special_tokens=False):
    t.add_tokens([' ' * n for n in reversed(range(n_min, n_max))],
                 special_tokens=as_special_tokens)
    return t


def include_tabs(t, n_min=2, n_max=20, as_special_tokens=False):
    t.add_tokens(['\t' * n for n in reversed(range(n_min, n_max))],
                 special_tokens=as_special_tokens)
    return t


def create_custom_gpt2_tokenizer():
    t = create_tokenizer()
    t = include_whitespace(t=t, n_min=2, n_max=32, as_special_tokens=False)
    t = include_tabs(t=t, n_min=2, n_max=10, as_special_tokens=False)
    return t


########################################################################
# sample

def sample(
    device,
    model,
    tokenizer,
    context,
    pad_token_id,
    num_return_sequences=1,
    temp=0.2,
    top_p=0.95,
    max_length_sample=128,
    max_length=2048
):

    input_ids = tokenizer(
        context,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors='pt',
    ).input_ids

    input_ids_len = input_ids.shape[1]
    assert input_ids_len < max_length

    with torch.no_grad():
        input_ids = input_ids.to(device)
        tokens = model.generate(
            input_ids,
            do_sample=True,
            num_return_sequences=num_return_sequences,
            temperature=temp,
            max_length=input_ids_len + max_length_sample,
            top_p=top_p,
            pad_token_id=pad_token_id,
            use_cache=True,
        )
        text = tokenizer.batch_decode(tokens[:, input_ids_len:, ...])

    return text


def truncate(completion):

    def find_re(string, pattern, start_pos):
        m = pattern.search(string, start_pos)
        return m.start() if m else -1

    terminals = [
        re.compile(r, re.MULTILINE)
        for r in
        [
            '^#',
            re.escape('<|endoftext|>'),
            "^'''",
            '^"""',
            '\n\n\n'
        ]
    ]

    prints = list(re.finditer('^print', completion, re.MULTILINE))
    if len(prints) > 1:
        completion = completion[:prints[1].start()]

    defs = list(re.finditer('^def', completion, re.MULTILINE))
    if len(defs) > 1:
        completion = completion[:defs[1].start()]

    start_pos = 0

    terminals_pos = [pos for pos in [find_re(
        completion, terminal, start_pos) for terminal in terminals] if pos != -1]
    if len(terminals_pos) > 0:
        return completion[:min(terminals_pos)]
    else:
        return completion


def test_truncate():

    assert truncate(
        '\nif len_a > len_b:\n    result = a\nelse:\n    result = b\n\n\n\n#') == '\nif len_a > len_b:\n    result = a\nelse:\n    result = b'


def load_model():
    global g_device
    global g_model
    global g_tokenizer
    global g_pad_token_id
    global g_batch_size
    global g_temp
    global g_top_p
    
    # (0) constants
    models_nl = ['codegen-350M-nl', 'codegen-2B-nl',
                 'codegen-6B-nl', 'codegen-16B-nl']
    models_pl = ['codegen-350M-multi', 'codegen-2B-multi', 'codegen-6B-multi', 'codegen-16B-multi',
                 'codegen-350M-mono', 'codegen-2B-mono', 'codegen-6B-mono', 'codegen-16B-mono']
    models = models_nl + models_pl

    # (1) preamble
    set_env()
    g_pad_token_id = 50256
    set_seed(42, deterministic=True)
    device = torch.device('cuda:0')
    use_fp16 = True
    model_name = "codegen-350M-nl"
    ckpt = f'./checkpoints/{model_name}'
    # (3) load
    with print_time('loading parameters'):
        model = create_model(ckpt=ckpt, fp16=use_fp16).to(device)
        if torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model, device_ids=[0, 1])

    with print_time('loading tokenizer'):
        if model_name in models_pl:
            tokenizer = create_custom_gpt2_tokenizer()
        else:
            tokenizer = create_tokenizer()
        tokenizer.padding_side = 'left'
        tokenizer.pad_token = g_pad_token_id
    if torch.cuda.device_count() > 1:
        g_model = model.module
    else:
        g_model = model
    g_device = device
    g_tokenizer = tokenizer
    g_batch_size = 1
    g_temp = 0.2
    g_top_p = 0.95
    
@lru_cache(maxsize=1024, typed=False)
def sampling(input_context,max_length):
    with print_time('sampling'):
        completion = sample(
            device=g_device,
            model=g_model,
            tokenizer=g_tokenizer,
            context=input_context,
            pad_token_id=g_pad_token_id,
            num_return_sequences=g_batch_size,
            temp=g_temp,
            top_p=g_top_p,
            max_length_sample=max_length)
        truncation = truncate(completion[0])
        return truncation

if __name__ == '__main__':
    test_truncate()
    load_model()
    print('done.')
