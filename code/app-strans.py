#!/usr/bin/env python3

from lxml import etree
from glob import glob
from tqdm import tqdm

import gradio as gr
from sentence_transformers import SentenceTransformer

from settings import threshold
from persist import find_embeddings, get_models
from results import render, pfa_templ

models = get_models()


def find(fulltext: str, m: str) -> str:
    response = find_embeddings(m, fulltext, 1 - threshold)
    result = [
        (r[0], pfa_templ.format(path=r[1], fname=r[2], addr=r[3]), r[4])
        for r in response
    ]
    return render(result)


demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox("Не осѫждаите да не осѫждени бѫдете", lines=5, label="Search"),
        gr.Dropdown(models, value="uaritm/multilingual_en_uk_pl_ru", label="Model"),
    ],
    outputs=[
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(
    server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/strans"
)
