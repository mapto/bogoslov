#!/usr/bin/env python3

from pathlib import Path
from difflib import SequenceMatcher

import gradio as gr

from settings import threshold
from persist import get_texts
from results import render_table, render_from_export, build_fname, pfa_templ


def find(fulltext: str) -> list[tuple[str, str, float]]:
    params = {"query": fulltext, "method": "lcs"}
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return render_from_export(fname_result)

    primary = get_texts()

    result = []
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
            result += [
                (
                    stripped,
                    pfa_templ.format(path=path, fname=filename, addr=address),
                    accuracy,
                )
            ]

    output = render_table(params, result)

    return output[0], output[1]


demo = gr.Interface(
    fn=find,
    description="""<h1>Longest Common Subsequence</h1><small>See <a href="http://www.eiti.uottawa.ca/~diana/publications/tkdd.pdf">Islam & Inkpen 2008</a></small>""",
    inputs=[
        gr.Textbox("Приде же въ градъ самарьскъ", lines=5, label="Search"),
    ],
    outputs=[
        gr.HTML(label="Download"),
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/lcs")
