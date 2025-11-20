#!/usr/bin/env python3

from pathlib import Path

import gradio as gr

from persist import find_regex, get_verse_text, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang, examples


def regex_escape(s: str) -> str:
    to_escape = "+?"
    if s in to_escape:
        return "\\" + s
    return s


subst = {}
skips = set()
with open(f"alphabet.{lang}.tsv", encoding="utf-8") as fal:
    for l in fal.readlines():
        # print(l[:-1].split("\t"))
        if " " in l[:-1].split("\t"):
            skips |= set(regex_escape(e) for e in l.split("\t")) - set([" "])

        elts = set(regex_escape(e.strip().lower()) for e in l.split("\t") if e.strip())

        for ch in elts:
            if ch not in subst:
                subst[ch] = set()
            subst[ch] |= elts

punct = elts
subst2 = {k: "|".join(sorted(v)) for k, v in subst.items()}


def generalize(s: str) -> str:
    """
    >>> generalize('-')
    '("|-|.|/|;|=|[|\\\\+|\\\\?|]|«|·|῀|—|’|⁘|⁜|∙|ⱖ|⸺|꙯|\ue049)?(◌҃)?'
    """
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


def find(sources: list[str], fulltext: str, match_case: bool, whole_words: bool) -> str:
    """
    The function that performs the search.
    Takes the query string as parameter and relevant regex flags.
    """
    pattern = generalize(fulltext)
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
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return pat, *render_from_export(fname_result)

    # see https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP
    op = "~" if match_case else "~*"

    matches = find_regex(pat, op, sources)

    result = [
        (
            get_verse_text(p, f, a),
            pfa_templ.format(path=p, fname=f, addr=a),
            1,
        )
        for p, f, a in matches
    ]

    output = render_table(params, result)

    return pat, *output


def interface() -> gr.Interface:
    sources = get_sources()

    app = gr.Interface(
        fn=find,
        description=f"""<h1>Regular Expressions</h1>
        <small>See <a href="https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP">Regular Expressions</a> in PostgreSQL,
        <a href="/alphabet.{lang}.tsv">equivalence table</a> and
        <a href="https://github.com/mapto/bogoslov/blob/main/code/app_regex.py#L44">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(min(examples, key=len), lines=5, label="Search"),
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
        css_paths=f"/static/{lang}.css",
    )

    return app


if __name__ == "__main__":
    app = interface()
    app.launch(
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/regex"
    )
