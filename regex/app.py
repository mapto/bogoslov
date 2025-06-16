#!/usr/bin/env python3

from lxml import etree
import regex as re

import gradio as gr
from glob import glob

primary_path = "/corpora/html/"

con_span = 100
"""
@font-face {
    font-family: 'CyrillicaOchrid10U';
    src: url('http://www.starobulglit.eu/OC10U.ttf') format('truetype');
}
@font-face{
    font-family:'KlimentStdWeb';
    src:url('http://bdinski.obdurodon.org/css/fonts/kliment_std-webfont.eot');
    src:url('http://bdinski.obdurodon.org/css/fonts/kliment_std-webfont.eot?#iefix') format('embedded-opentype'), 
        url('http://bdinski.obdurodon.org/css/fonts/kliment_std-webfont.woff') format('woff'), 
        url('http://bdinski.obdurodon.org/css/fonts/kliment_std-webfont.ttf') format('truetype'), 
        url('http://bdinski.obdurodon.org/css/fonts/kliment_std-webfont.svg#KlimentStdRegular') format('svg');
    font-weight:normal;
    font-style:normal;
}
@font-face{
    font-family:'BukyvedeWeb';
    src:url('http://bdinski.obdurodon.org/css/fonts/bukyvede-regular-webfont.eot');
    src:url('http://bdinski.obdurodon.org/css/fonts/bukyvede-regular-webfont.eot?#iefix') format('embedded-opentype'), 
        url('http://bdinski.obdurodon.org/css/fonts/bukyvede-regular-webfont.woff') format('woff'), 
        url('http://bdinski.obdurodon.org/css/fonts/bukyvede-regular-webfont.ttf') format('truetype'), 
        url('http://bdinski.obdurodon.org/css/fonts/bukyvede-regular-webfont.svg#BukyvedeRegular') format('svg');
    font-weight:normal;
    font-style:normal;

}
"""

# <html><head>
html_head = """<style>
@font-face{
	font-family:BukyVede;
	src:url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Regular.ttf) format('truetype'),
		url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Bold.ttf) format('truetype'),
		url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Italic.ttf) format('truetype')
}

.quote {
    font-family: BukyVede !important;
}
.match {
    background:yellow;
}
</style>"""

css = """
@font-face{
    font-family:BukyVede;
    src:url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Regular.ttf) format('truetype'),
        url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Bold.ttf) format('truetype'),
        url(http://scripta-bulgarica.eu/sites/all/themes/scripta/fonts/BukyVede-Italic.ttf) format('truetype')
}

.quote {
    font-family: BukyVede !important;
}

.match {
    background:yellow;
}

footer {
    visibility: hidden;
}
"""



srcs = glob(f"{primary_path}/*/*.html")

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
    "PROIEL (Sinai Psalter, Codex Marianus)",
    "WikiSource (Codex Marianus, Codex Zographensis)",
    "MacRobert (Bologna Psalter)",
]
books = ["Psalter", "Matthew", "Mark", "Luke", "John"]

# files = {"PROIEL": "proiel_20180408", "WikiSource": "wikisource_20250407"}

corpus_labels = {
    "macrobert_20250303_psal-bol": "Bologna Psalter from Mary MacRobert",
    "torot_20180919_psal-sin": "Sinai Psalter from TOROT",
    "proiel_20180408_marianus_matthew": "Codex Marianus - Matthew from PROIEL",
    "proiel_20180408_marianus_mark": "Codex Marianus - Mark from PROIEL",
    "proiel_20180408_marianus_luke": "Codex Marianus - Luke from PROIEL",
    "proiel_20180408_marianus_john": "Codex Marianus - John from PROIEL",
    "wikisource_20250407_marianus_matthew": "Codex Marianus - Matthew from WikiSource",
    "wikisource_20250407_marianus_mark": "Codex Marianus - Mark from WikiSource",
    "wikisource_20250407_marianus_luke": "Codex Marianus - Luke from WikiSource",
    "wikisource_20250407_marianus_john": "Codex Marianus - John from WikiSource",
    "wikisource_20250407_zogr_matthew": "Codex Zographensis - Matthew from WikiSource",
    "wikisource_20250407_zogr_mark": "Codex Zographensis - Mark from WikiSource",
    "wikisource_20250407_zogr_luke": "Codex Zographensis - Luke from WikiSource",
    "wikisource_20250407_zogr_john": "Codex Zographensis - John from WikiSource",
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
    res = res.replace(" ", "\s+")
    return res


def select_sources(sources, books):
    # TODO: Any other sources than Bologna Psalter
    result = []
    src = [s.split(" ")[0] for s in sources]
    for b in books:
        if b == "Psalter":
            if "MacRobert" in src:
                result += ["Bologna Psalter"]
            if "PROIEL" in src:
                result += ["torot_20180919_psal-sin"]
        else:
            if "PROIEL" in src:
                result += [f"proiel_20180408_marianus_{b.lower()}"]
            if "WikiSource" in src:
                result += [
                    f"wikisource_20250407_marianus_{b.lower()}",
                    f"wikisource_20250407_zogr_{b.lower()}",
                ]
    return result


def render(data: dict[str, list[str]]) -> str:
    result_templ = """<li>
    <span class='locator'>{locator}:</span>
    <span class='quote'>
        {prefix}<span class='match'>{match}</span>{suffix}
    </span>
</li>"""
    href_templ = """<a href="{href}" target="fulltext">{content}</a>"""

    result = []
    for addr, insts in data.items():
        if not insts:
            continue
        htmls = [
            result_templ.format(locator=l, prefix=p, match=m, suffix=s)
            for l, p, m, s in insts
        ]
        contents = "\n".join(htmls)
        href = f"/corpora/{addr}"
        hr_addr = addr.replace("/", ":").replace(".html#", ":")
        result += [
            f"{href_templ.format(href=href, content=hr_addr)}:<ul>{contents}</ul>"
        ]
    return "<br/>".join(result)


def find(
    s: str,
    # sources: list[str],
    # books: list[str],
    context: int = 10,
    ignore_case: bool = True,
    whole_words: bool = False,
) -> str:
    sources = ["MacRobert"]
    books = ["Psalter"]
    srcs = select_sources(sources, books)

    pattern = generalise(s)
    noword = (
        "(\s|"
        + "|".join((f"\\{p}" if p in "?+.[]-=" else p) for p in punct if p)
        + ")+"
    )
    pat = (noword + pattern + noword) if whole_words else pattern

    flags = re.DOTALL
    flags |= re.IGNORECASE if ignore_case else 0

    result = {}
    for kid, text in texts.items():
        if not any(kid.startswith(s) for s in srcs):
            continue
        # print(kid)
        # print(text)
        res = re.finditer(pat, text, flags=flags)
        # print(bool(res), res)
        result[kid] = [
            (
                f"[{r.start()}-{r.end()}]",
                f"{text[max(r.start()-context,0):r.start()]}",
                f"{text[r.start():r.end()]}",
                f"{text[r.end():min(r.end()+context,len(text)-1)]}",
            )
            for r in res
        ]

    return pat, render(result)


# def html_wrap(text: str) -> str:
#     return html_prefix + text + html_suffix

# find("бог", 20, whole_words=True)

demo = gr.Interface(
    fn=find,
    inputs=[
        gr.Textbox("бог", label="Search"),
        # gr.CheckboxGroup(
        #     choices=sources,
        #     value=sources,
        #     label="Sources",
        # ),
        # gr.CheckboxGroup(
        #     choices=books,
        #     value=books,
        #     label="Books",
        # ),
        gr.Radio([20, 50, 100, 200], value=200, label="Letters in context"),
        gr.Checkbox(label="Match case"),
        gr.Checkbox(label="Whole words"),
    ],
    # outputs=[gr.Textbox(label="Results", head=html_head)],
    # outputs=[gr.Blocks(label="Results")],
    outputs=[
        gr.Textbox(
            "", label="Regex to paste in https://debuggex.com to interpret results"
        ),
        gr.HTML(label="Results"),
    ],
    css=css,
    # head=html_head,
)

# demo.launch(share=True)
# demo.launch(server_port=8000, server_name='0.0.0.0')

demo.launch(server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/regex")
