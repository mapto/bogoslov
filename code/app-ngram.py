#!/usr/bin/env python3

from lxml import etree
from glob import glob

import gradio as gr

from udpipeclient import udpipe_sent_lemmatize

# from stanzacilent import stanza_sent_lemmatize

from db import Session

# from model import Verse

from util import get_ngrams
from persist import find_ngram

from settings import static_path

sent_stemmers = {
    "dummy": lambda x: [(t, t) for t in tokenizer(x) if t.strip()],
    # "stanza": stanza_sent_lemmatize,
    "udpipe": udpipe_sent_lemmatize,
}

stemmer = "udpipe"
# stemmer = "stanza"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"


def ids2hrefs(ids: list[str]) -> str:
    href_templ = """<li><a href="{href}" target="fulltext">{label}</a></li>"""
    return "\n".join(
        href_templ.format(
            label=nid.replace(".tei.xml#", ":").replace(".", ":").replace("_", "."),
            href=f"{static_path}{nid.replace('.tei.xml', '.html')}",
        )
        for nid in ids
    )


def render(data: list[tuple[str, list[str]]]) -> str:
    """a list of <text ngram, list of addresses>"""
    if not data:
        return "Result is empty."
    result = []
    # print(data)
    for ngram, addresses in data:
        result += [f"'{ngram}':<ul>{ids2hrefs(addresses)}</ul>"]
    return "<br/>".join(result)


def find(fulltext: str, n: int = 4) -> str:
    ltext = " ".join(l for w, l in sent_stemmers[stemmer](fulltext))
    if len(ltext.split(" ")) < n:
        return "", "Not enough tokens provided to search for N-grams"

    try:
        new_ngrams = get_ngrams(fulltext, ltext, n)
    except AssertionError as ae:
        return ltext, f"Cannot make n-grams. {ae}"
    # print(new_ngrams)
    # print(ngrams)

    result = []
    # print(new_ngrams)
    for kng, vtloc in new_ngrams.items():
        for estart, eend, etext in vtloc:
            nxt = find_ngram(n, ",".join(kng), estart, eend, etext)
            result += [
                (
                    etext,
                    [f"{path}/{filename}#{address}" for path, filename, address in nxt],
                )
            ]

    return ltext, render(result)


demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox(
            "Блаженъ мѫжъ иже не иде на съвѣть нечъстивъїхъ", lines=5, label="Search"
        ),
        # gr.Radio(
        #     choices=sent_stemmers.keys(),
        #     value="stanza",
        #     label="Lemmatizer",
        # ),
        gr.Slider(minimum=2, maximum=10, value=3, step=1, label="N-gram"),
    ],
    outputs=[
        gr.Textbox(label="Lemmatized"),
        gr.HTML(label="Results"),
    ],
    # css=css,
    # head=html_head,
)

# demo.launch(share=True)
# demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False)
# demo.launch()

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/ngram")
