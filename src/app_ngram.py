#!/usr/bin/env python3

from pathlib import Path
from collections import Counter
import random
import logging

import gradio as gr

from settings import ng_min, ng_max, ng_default, threshold_ngram
from util import get_ngrams
from persist import find_ngram, get_verse_text, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang, examples
from lemmatizer import lemmatizer

logger = logging.getLogger(__name__)

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"


def find(
    sources: list[str],
    fulltext: str,
    lemmatized: list[tuple[str, str]] = [],
    n: int = 0,
) -> list[tuple[str, str, float]]:
    """
    The function that performs the search.
    Takes the query string as parameter and the lenght of the (word token) n-gram.
    """
    logger.debug(f"Starting {__name__}")
    if not lemmatized:
        lemmatized = lemmatizer(fulltext)
    if not n:
        ln = len(lemmatized)
        if ln > 6:
            n = 3
        elif ln > 3:
            n = 2
        else:
            n = 1

    ltext = " ".join(lem for w, lem in lemmatized)

    try:
        new_ngrams = get_ngrams(fulltext, ltext, n)
    except AssertionError as ae:
        logger.error(repr(ae))
        return []

    # print(new_ngrams)
    ngrams_counter = Counter()  # type: ignore
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
            acc,
        )
        for p, f, a in ngrams_counter.keys()
        if (acc := ngrams_counter[(p, f, a)] / (len(lemmatized) - n + 1))
        >= threshold_ngram
        # if ngrams_counter[(p, f, a)] / (len(lemmatized) - n+1) >= threshold
    ]

    return result


def wrapper(sources: list[str], fulltext: str, n: int) -> tuple[str, str, str]:
    lemmatized = lemmatizer(fulltext)
    if not n:
        ln = len(lemmatized)
        if ln > 6:
            n = 3
        elif ln > 3:
            n = 2
        else:
            n = 1

    ltext = " ".join(lem for w, lem in lemmatized)
    if len(lemmatized) < n:
        return (
            ltext,
            (
                "Not enough tokens provided to search for N-grams. "
                "Maybe try Regex istead? "
                f"Tokens identified: {len(lemmatized)}. If this is wrong, consider simplifying your query."
            ),
            "",
        )

    params = {
        "query": fulltext,
        "method": "ngram",
        "n": str(n),
        "lemmatized": ltext,
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return ltext, *render_from_export(fname_result)

    result = find(sources, fulltext, lemmatized)
    output = render_table(params, result)

    return ltext, *output


def interface() -> gr.Interface:
    sources = get_sources()

    app = gr.Interface(
        fn=wrapper,
        description="""<h1>Lemmatized N-grams</h1><small>See <a href="https://stephanus.tlg.uci.edu/helppdf/ngrams.pdf">N-grams in TLG</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app_ngram.py#L32">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(random.choice(examples), lines=5, label="Search"),
            # gr.Radio(
            #     choices=sent_stemmers.keys(),
            #     value="stanza",
            #     label="Lemmatizer",
            # ),
            gr.Slider(
                minimum=ng_min, maximum=ng_max, value=ng_default, step=1, label="N-gram"
            ),
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
