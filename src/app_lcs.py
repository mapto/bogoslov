#!/usr/bin/env python3

from pathlib import Path
from difflib import SequenceMatcher
import random

import gradio as gr

from settings import threshold_lcs
from persist import get_texts, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang, examples


def find(
    sources: list[str], fulltext: str, match_case: bool = False
) -> list[tuple[str, str, float]]:
    """
    The function that performs the search.
    Takes the query string as parameter.
    """
    primary = get_texts(sources)

    result = []
    textlen = len(fulltext)
    stext = fulltext if match_case else fulltext.lower()
    for path, filename, address, t in primary:
        st = t if match_case else t.lower()
        s = SequenceMatcher(None, stext, st)

        blocks = [b for b in s.get_matching_blocks() if b.size]
        if blocks:
            stripped = st[blocks[0].b : (blocks[-1].b + blocks[-1].size)]
        else:
            stripped = st

        lcs = "".join([fulltext[b.a : (b.a + b.size)] for b in blocks])
        accuracy = (2 * len(lcs)) / (textlen + len(stripped))
        if accuracy >= threshold_lcs:
            result += [
                (
                    stripped,
                    pfa_templ.format(path=path, fname=filename, addr=address),
                    accuracy,
                )
            ]

    return result


def wrapper(sources: list[str], fulltext: str, match_case: bool) -> tuple[str, str]:
    params = {
        "query": fulltext,
        "method": "lcs",
        "match case": str(match_case),
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return render_from_export(fname_result)

    result = find(sources, fulltext, match_case)
    output = render_table(params, result)

    return output


def interface() -> gr.Interface:
    sources = get_sources()

    app = gr.Interface(
        fn=wrapper,
        description="""<h1>Longest Common Subsequence</h1><small>See <a href="http://www.eiti.uottawa.ca/~diana/publications/tkdd.pdf">Islam & Inkpen 2008</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app_lcs.py#L13">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(random.choice(examples), lines=5, label="Search"),
            gr.Checkbox(label="Match case"),
        ],
        outputs=[
            gr.HTML(label="Download"),
            gr.HTML(label="Results"),
        ],
        css_paths=f"/static/{lang}.css",
    )

    return app


if __name__ == "__main__":
    app = interface()
    app.launch(
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/lcs"
    )
