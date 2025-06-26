#!/usr/bin/env python3

from lxml import etree
from glob import glob
from tqdm import tqdm

import gradio as gr
from sentence_transformers import SentenceTransformer

from persist import find_embeddings, get_models

from settings import static_path

models = get_models()

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"


def render(data: dict[str, list[str]]) -> str:
    result_templ = """<li><span class='quote'>{text}</span></li>"""
    href_templ = """<a href="{href}" target="fulltext">{content}</a>"""

    result = []
    for addr, texts in data.items():
        if not texts:
            continue
        htmls = [result_templ.format(text=t) for t in texts]
        contents = "\n".join(htmls)
        href = f"{static_path}{addr}".replace("tei.xml", "html")
        hr_addr = addr.replace("/", ".").replace(".html#", ":")
        result += [
            f"{href_templ.format(href=href, content=hr_addr)}:<ul>{contents}</ul>"
        ]
    return "<br/>".join(result)


def find(fulltext: str, m: str) -> str:
    result = find_embeddings(m, fulltext)
    data = {}
    for addr, text in result:
        if addr not in data:
            data[addr] = []
        data[addr] += [text]

    return render(data)


demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox(
            "Не осѫждаите да не осѫждени бѫдете", lines=5, label="Search"
        ),
        gr.Dropdown(models, value="uaritm/multilingual_en_uk_pl_ru", label="Model"),
    ],
    outputs=[
        gr.HTML(label="Results"),
    ],
)

demo.launch(
    server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/strans"
)
