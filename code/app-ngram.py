#!/usr/bin/env python3

from pathlib import Path
from collections import Counter

import gradio as gr

from udpipeclient import udpipe_sent_lemmatize

# from stanzacilent import stanza_sent_lemmatize

from settings import max_ngram
from util import get_ngrams
from persist import find_ngram, get_verse_text, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang

sent_stemmers = {
    "dummy": lambda x: [(t, t) for t in tokenizer(x) if t.strip()],
    # "stanza": stanza_sent_lemmatize,
    "udpipe": udpipe_sent_lemmatize,
}

stemmer = "udpipe"
# stemmer = "stanza"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"


def find(sources: list[str], fulltext: str, n: int = 4) -> str:
    """
    The function that performs the search.
    Takes the query string as parameter and the lenght of the (word token) n-gram.
    """
    lemmatized = sent_stemmers[stemmer](fulltext)
    ltext = " ".join(lem for w, lem in lemmatized)
    if len(lemmatized) < n:
        return (
            ltext,
            "Not enough tokens provided to search for N-grams",
            f"Tokens identified: {len(lemmatized)}. If this is wrong, consider simplifying your query.",
        )

    params = {
        "query": fulltext,
        "method": "ngram",
        "n": n,
        "lemmatized": ltext,
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return ltext, *render_from_export(fname_result)

    try:
        new_ngrams = get_ngrams(fulltext, ltext, n)
    except AssertionError as ae:
        return ltext, f"Cannot make n-grams. {ae}", str(ae)
    # print(new_ngrams)
    # print(ngrams)

    # print(new_ngrams)
    ngrams_counter = Counter()
    for kng, vtloc in new_ngrams.items():
        for estart, eend, etext in vtloc:
            nxt = find_ngram(n, ",".join(kng), estart, eend, etext, sources)
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

    output = render_table(params, result)

    return ltext, *output


def interface() -> gr.Interface:
    sources = get_sources()

    app = gr.Interface(
        fn=find,
        description="""<h1>Lemmatized N-grams</h1><small>See <a href="https://stephanus.tlg.uci.edu/helppdf/ngrams.pdf">N-grams in TLG</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app-ngram.py#L32">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(
                "въса землꙗ да поклонит ти се и поеть тебе", lines=5, label="Search"
            ),
            # gr.Radio(
            #     choices=sent_stemmers.keys(),
            #     value="stanza",
            #     label="Lemmatizer",
            # ),
            gr.Slider(minimum=2, maximum=max_ngram, value=3, step=1, label="N-gram"),
        ],
        outputs=[
            gr.Textbox(label="Lemmatized"),
            gr.HTML(label="Download"),
            gr.HTML(label="Results"),
        ],
        css_paths=f"/static/{lang}.css",
    )

    return app


if __name__ == "__main__":
    app = interface()
    app.launch(
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/ngram"
    )
