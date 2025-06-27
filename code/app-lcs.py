#!/usr/bin/env python3

from difflib import SequenceMatcher

import gradio as gr

from settings import threshold
from persist import get_texts
from results import render


def find(fulltext: str) -> list[tuple[str, str, float]]:
    primary = get_texts()

    results = []
    textlen = len(fulltext)
    for path, filename, address, t in primary:
        s = SequenceMatcher(None, fulltext, t)

        blocks = [b for b in s.get_matching_blocks() if b.size]
        if blocks:
            stripped = t[blocks[0].b : (blocks[-1].b + blocks[-1].size)]
        else:
            stripped = t

        lcs = "".join([fulltext[b.a : (b.a + b.size)] for b in blocks])
        accuracy = (2 * len(lcs)) / (textlen + len(stripped))
        if accuracy >= threshold:
            results += [(stripped, f"{path}/{filename}#{address}", accuracy)]

    return render(results)


demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox("Приде же въ градъ самарьскъ", lines=5, label="Search"),
    ],
    outputs=[
        # gr.Textbox(label="Lemmatized"),
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/lcs")
