#!/usr/bin/env python3

from lxml import etree
from glob import glob

import gradio as gr

from udpipeclient import udpipe_sent_lemmatize
# from stanzacilent import stanza_sent_lemmatize

from util import get_ngrams

static_path = "/corpora/"

sent_stemmers = {
    "dummy": lambda x: [(t, t) for t in tokenizer(x) if t.strip()],
    # "stanza": stanza_sent_lemmatize,
    "udpipe": udpipe_sent_lemmatize,
}

stemmer = "udpipe"
# stemmer = "stanza"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

# stemmer = "udpipe"
# src = f"*{stemmer}/*.tei.xml"
src = f"/corpora/{stemmer}/*/*.tei.xml"

data = {}
for fname in glob(src):
    print(fname)
    corpus = fname.split("/")[-2]
    ch = fname.split("/")[-1]
    root = etree.parse(fname)
    result = root.xpath(f"//tei:{unit}", namespaces=ns)
    for e in result:
        eid = e.get("id")
        data[f"{corpus}/{ch}#{eid}"] = " ".join(
            e.xpath(f"""//tei:{unit}[@id='{eid}']//tei:w/@lemma""", namespaces=ns)
        )


def ids2hrefs(ids: list[str]) -> str:
    href_templ = """<li><a href="{href}">{label}</a></li>"""
    return "\n".join(
        href_templ.format(
            label=nid.replace("/", ":").replace(".tei.xml#", ":").replace("_", "."),
            href=f"{static_path}{nid.replace('.tei.xml', '.html')}",
        )
        for nid in ids
    )


def render(data: list[tuple[str, list[str]]]) -> str:
    """a list of <text ngram, list of addresses>"""
    result = []
    for ngram, addresses in data:
        result += [f"'{ngram}':<ul>{ids2hrefs(addresses)}</ul>"]
    return "<br/>".join(result)


def find(fulltext: str, n: int = 4) -> str:
    ngrams = {}
    for kid, vtext in data.items():
        lemmas = [l for l in vtext.split(" ") if l]
        for i in range(len(lemmas) - n + 1):
            ng = tuple(lemmas[i : i + n])
            if ng not in ngrams:
                ngrams[ng] = []
            ngrams[ng] += [kid]

    ltext = " ".join(w for w, l in sent_stemmers[stemmer](fulltext))
    assert len(ltext.split(" ")) >= n, "Not enough tokens provided to search N-grams"

    try:
        new_ngrams = get_ngrams(fulltext, ltext, n)
    except AssertionError:
        return (
            f"Lemmatizer cannot lemmatize.<br/>Sentence: {fulltext}<br/>Lemmas: {ltext}"
        )
    # print(new_ngrams)
    # print(ngrams)

    result = []
    for kng, vtloc in new_ngrams.items():
        if kng in ngrams:
            # print(f"{v}:\t{ngrams[k]}")
            for estart, eend, etext in vtloc:
                result += [(etext, ngrams[kng])]

    return render(result)


demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox(
            "блаженъ мѫжь иже не ити на съвѣть нечьстивъ", lines=5, label="Search"
        ),
        # gr.Radio(
        #     choices=sent_stemmers.keys(),
        #     value="stanza",
        #     label="Lemmatizer",
        # ),
        # gr.Textbox("*{stemmer}/BM*.tei.xml"),
        gr.Slider(minimum=3, maximum=7, value=4, step=1, label="N-gram"),
    ],
    # outputs=[gr.Textbox(label="Results", head=html_head)],
    # outputs=[gr.Blocks(label="Results")],
    outputs=[
        gr.HTML(label="Results"),
    ],
    # css=css,
    # head=html_head,
)

# demo.launch(share=True)
# demo.launch(server_port=8000, server_name='0.0.0.0')
# demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False)
# demo.launch()

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/ngram")
