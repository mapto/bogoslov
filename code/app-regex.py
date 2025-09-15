#!/usr/bin/env python3

from pathlib import Path
from lxml import etree
import regex as re

import gradio as gr
from glob import glob

from settings import static_path
from persist import find_regex, get_verse_text
from results import render_table, render_from_export, build_fname, pfa_templ

subst = {}
skips = set()
with open("alphabet.tsv", encoding="utf-8") as fal:
    for l in fal.readlines():
        # print(l[:-1].split("\t"))
        if " " in l[:-1].split("\t"):
            skips |= set(l.split("\t")) - set([" "])
        elts = set(e.strip().lower() for e in l.split("\t") if e.strip())
        for ch in elts:
            if ch not in subst:
                subst[ch] = set()
            subst[ch] |= elts

punct = elts
subst2 = {k: "|".join(v) for k, v in subst.items()}


def generalise(s: str) -> str:
    res = s.lower()
    for i, (k, v) in enumerate(subst2.items()):
        res = res.replace(k, f"({i})")
    for i, (k, v) in enumerate(subst2.items()):
        if k in skips:
            res = res.replace(f"({i})", f"({v})?(◌҃)?")
        else:
            res = res.replace(f"({i})", f"({v})(◌҃)?")
    res = res.replace(" ", r"\s+")
    return res


def find(fulltext: str, match_case: bool, whole_words: bool) -> str:
    pattern = generalise(fulltext)
    noword = (
        r"(\s|"
        + "|".join((f"\\{p}" if p in "?+.[]-=" else p) for p in punct if p)
        + ")+"
    )
    pat = (noword + pattern + noword) if whole_words else pattern

    params = {
        "query": fulltext,
        "method": "regex",
        "match case": match_case,
        "whole words": whole_words,
        "pattern": pat,
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return render_from_export(fname_result)

    # see https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP
    op = "~" if match_case else "~*"

    matches = find_regex(pat, op)

    result = [
        (
            get_verse_text(p, f, a),
            pfa_templ.format(path=p, fname=f, addr=a),
            1,
        )
        for p, f, a in matches
    ]

    output = render_table(params, result)

    return pat, output[0], output[1]


demo = gr.Interface(
    fn=find,
    description="""<h1>Regular Expressions</h1><small>See <a href="https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP">Regular Expressions</a> in PostgreSQL</small>""",
    inputs=[
        gr.Textbox("богомъ", label="Search"),
        gr.Checkbox(label="Match case"),
        gr.Checkbox(label="Whole words"),
    ],
    # outputs=[gr.Textbox(label="Results", head=html_head)],
    # outputs=[gr.Blocks(label="Results")],
    outputs=[
        gr.Textbox(
            "", label="Regex to paste in https://debuggex.com to interpret results"
        ),
        gr.HTML(label="Download"),
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/regex")
