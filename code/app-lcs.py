#!/usr/bin/env python3

from difflib import SequenceMatcher

import gradio as gr

from persist import get_texts

from settings import static_path, threshold


def render(data: list[tuple[str, str, float]]) -> str:
    """a list of <text, address, accuracy>"""
    href_templ = """<a href="{href}" target="fulltext">{label}</a>"""

    data.sort(key=lambda x: x[2], reverse=True)
    if not data:
        return "Result is empty."
    result = []
    # print(data)
    for text, address, accuarcy in data:
        link = href_templ.format(
            label=address.replace(".tei.xml#", ":").replace(".", ":").replace("_", "."),
            href=f"{static_path}{address.replace('.tei.xml', '.html')}",
        )
        result += [f"<li>{link} [{accuarcy:.4f}]: {text}</li>"]
    return "<br/>".join(result)


def find(fulltext: str) -> list[tuple[str, str, float]]:
    primary = get_texts()

    results = []
    textlen = len(fulltext)
    for path, filename, address, t in primary:
        s = SequenceMatcher(None, fulltext, t)

        lcs = "".join(
            [
                fulltext[block.a : (block.a + block.size)]
                for block in s.get_matching_blocks()
            ]
        )
        accuracy = len(lcs) / textlen
        if accuracy >= threshold:
            results += [(t, f"{path}/{filename}#{address}", accuracy)]

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
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/lcs")
