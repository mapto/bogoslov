#!/usr/bin/env python3

from lxml import etree
from glob import glob
from collections import Counter

import gradio as gr

from udpipeclient import udpipe_sent_lemmatize

# from stanzacilent import stanza_sent_lemmatize

from db import Session
from settings import static_path, threshold
from util import get_ngrams
from persist import find_ngram, get_verse_text
from results import render_table, pfa_templ, href_templ

sent_stemmers = {
    "dummy": lambda x: [(t, t) for t in tokenizer(x) if t.strip()],
    # "stanza": stanza_sent_lemmatize,
    "udpipe": udpipe_sent_lemmatize,
}

stemmer = "udpipe"
# stemmer = "stanza"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"


def find(fulltext: str, n: int = 4) -> str:
    lemmatized = sent_stemmers[stemmer](fulltext)
    ltext = " ".join(l for w, l in lemmatized)
    if len(lemmatized) < n:
        return "", "Not enough tokens provided to search for N-grams"

    try:
        new_ngrams = get_ngrams(fulltext, ltext, n)
    except AssertionError as ae:
        return ltext, f"Cannot make n-grams. {ae}"
    # print(new_ngrams)
    # print(ngrams)

    found = []
    # print(new_ngrams)
    ngrams_total = len(new_ngrams)
    ngrams_counter = Counter()
    for kng, vtloc in new_ngrams.items():
        for estart, eend, etext in vtloc:
            nxt = find_ngram(n, ",".join(kng), estart, eend, etext)
            ngrams_counter += Counter(nxt)
            # for path, fname, addr in nxt:
            #     ngrams_counter[(path, fname, addr)] += 1

    result = [
        (
            get_verse_text(p, f, a),
            pfa_templ.format(path=p, fname=f, addr=a),
            ngrams_counter[(p, f, a)] / (len(lemmatized) - n + 1),
        )
        for p, f, a in ngrams_counter.keys()  # if ngrams_counter[(p, f, a)] / (len(lemmatized) - n+1) >= threshold
    ]

    output = render_table(
        {"query": fulltext, "method": "n-gram", "n": n, "lemmatized": ltext},
        result,
    )

    return ltext, output[0], output[1]


demo = gr.Interface(
    fn=find,
    description="""<h1>Lemmatized N-grams</h1><small>See <a href="https://stephanus.tlg.uci.edu/helppdf/ngrams.pdf">N-grams in TLG</a></small>""",
    inputs=[
        gr.Textbox(
            "въса землꙗ да поклонит ти се и поеть тебе", lines=5, label="Search"
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
        gr.HTML(label="Download"),
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/ngram")
