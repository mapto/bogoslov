#!/usr/bin/env python3

from pathlib import Path
import random
import logging

import bm25s
import gradio as gr
from fuzzywuzzy import fuzz

from lemmatizer import lemmatizer
from persist import get_texts, get_sources, get_lemmas
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang, examples, threshold_bm25

logger = logging.getLogger(__name__)

def stemWords(tokens: list[str]) -> list[str]:
    text = " ".join(tokens)
    res = get_lemmas(text)
    if not res:
        udres = lemmatizer(text)
        res = [lem for _, lem in udres]
    return res


def find(sources: list[str], fulltext: str) -> list[tuple[str, str, float]]:
    logger.debug(f"Starting {__name__}")
    primary = get_texts(sources)

    retriever = bm25s.BM25()

    addresses = {t: pfa_templ.format(path=p, fname=f, addr=a) for p, f, a, t in primary}
    corpus = [t for p, f, a, t in primary]

    # Tokenize the corpus and only keep the ids (faster and saves memory)
    corpus_tokens = bm25s.tokenize(corpus, stemmer=stemWords)

    # Create the BM25 model and index the corpus
    retriever.index(corpus_tokens)

    # Query the corpus
    query_tokens = bm25s.tokenize(fulltext, stemmer=stemWords)

    # Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k).
    # To return docs instead of IDs, set the `corpus=corpus` parameter.
    results, scores = retriever.retrieve(query_tokens, k=threshold_bm25, corpus=corpus)

    coef = fuzz.ratio(fulltext, results[0, 0]) / (100 * scores[0, 0])

    result = [
        (results[0, i], addresses[results[0, i]], (scores[0, i] * coef))
        for i in range(results.shape[1])
    ]

    return result


def wrapper(sources: list[str], fulltext: str) -> tuple[str, str, str]:
    lemmatized = lemmatizer(fulltext)
    ltext = " ".join(lem for w, lem in lemmatized)

    params = {
        "query": fulltext,
        "method": "bm25",
        "sources": sources2code(sources),
    }

    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return ltext, *render_from_export(fname_result)

    result = find(sources, fulltext)
    output = render_table(params, result)

    return ltext, *output


def interface() -> gr.Interface:
    sources = get_sources()

    app = gr.Interface(
        fn=wrapper,
        description="""<h1>Best Match 25</h1><small>See <a href="https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf">Robertson & Zaragoza 2009</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app_bm25.py#L13">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(random.choice(examples), lines=5, label="Search"),
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
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/bm25"
    )
