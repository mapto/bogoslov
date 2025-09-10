#!/usr/bin/env python3

from lxml import etree
import regex as re

import gradio as gr
from glob import glob

from settings import static_path
from persist import find_regex, get_verse_text
from results import render, render_table, pfa_templ, href_templ

con_span = 100


srcs = glob(f"{static_path}*/*.html")

texts = {}
parser = etree.HTMLParser()
for fname in srcs:
    print(fname)
    corpus = fname.split("/")[-2]
    ch = fname.split("/")[-1]
    root = etree.parse(fname, parser)
    result = root.xpath(f"//div[@class='chapter']")
    for e in result:
        eid = e.get("id")
        xpath = f"""//div[@id='{eid}']//span/text()"""
        text = " ".join(e.xpath(xpath))
        texts[f"{corpus}/{ch}#{eid}"] = text.strip()
        # print(xpath)
        # print(text)

sources = [
    "Sintacticus (Sinai Psalter, Codex Marianus, Codex Zographensis)",
    # "WikiSource (Codex Marianus, Codex Zographensis)",
    "Oxford (Bologna Psalter)",
]
books = ["Psalter", "Matthaeo", "Marco", "Luca", "Ioanne"]

corpus_labels = {
    "psalter.bologna.oxford": "Bologna Psalter from Catherine Mary MacRobert",
    "psalter.sinai.syntacticus": "Sinai Psalter from Syntacticus",
    "gospel.marianus.syntacticus": "Codex Marianus from Syntacticus",
    "gospel.zographensis.syntacticus": "Codex Zographensis from Syntacticus",
    "gospel.marianus.wikisource": "Codex Marianus from WikiSource",
    "gospel.zographensis.wikisource": "Codex Zographensis from WikiSource",
}

corpus_files = {v: k for k, v in corpus_labels.items()}


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


def find(
    s: str,
    # sources: list[str],
    # books: list[str],
    # context: int = 10,
    ignore_case: bool = True,
    whole_words: bool = False,
) -> str:

    pattern = generalise(s)
    noword = (
        r"(\s|"
        + "|".join((f"\\{p}" if p in "?+.[]-=" else p) for p in punct if p)
        + ")+"
    )
    pat = (noword + pattern + noword) if whole_words else pattern
    op = '~' if ignore_case else '~*'  # see https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP

    matches = find_regex(pat, op)

    result = [
        (
            get_verse_text(p, f, a),
            pfa_templ.format(path=p, fname=f, addr=a),
            1,
        )
        for p, f, a in matches
    ]

    # output = render(result)
    output = render_table({"query": s, "ignore case": ignore_case, "whole words": whole_words}, result)
    return pat, output[1]
    return pat, output[0], output[1]
    # return pat, output, None
    # return pat, output[0], None


demo = gr.Interface(
    fn=find,
    description="""<h1>Regular Expressions</h1><small>See <a href="https://www.postgresql.org/docs/17/functions-matching.html#FUNCTIONS-POSIX-REGEXP">Regular Expressions</a> in PostgreSQL</small>""",
    inputs=[
        gr.Textbox("бог", label="Search"),
        gr.Checkbox(label="Match case"),
        gr.Checkbox(label="Whole words"),
    ],
    # outputs=[gr.Textbox(label="Results", head=html_head)],
    # outputs=[gr.Blocks(label="Results")],
    outputs=[
        gr.Textbox(
            "", label="Regex to paste in https://debuggex.com to interpret results"
        ),
        # gr.DownloadButton(label="Download"),
        gr.HTML(label="Results"),
    ],
    css_paths="/static/ocs.css",
)

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/regex")
