import hashlib
from urllib.parse import quote_plus

import pandas as pd
from openpyxl.styles import Alignment, Font

from settings import static_path, base_url


pfa_templ = "{path}/{fname}#{addr}"
# fname_templ = "/results/{params}.xlsx"
fname_templ = "/results/{method}-{params}.xlsx"
# fname_templ = "/results/{query}-{method}-{params}.xlsx"

table_templ = """<table class="results">{body}</table>"""
trow_templ = """<tr><td class="quote">{text}</td><td class="info"><span title="accuracy" style="font-size: large; opacity: {acc}">{acc}</span><br><a href="{href}" title="{urn}">{ref}<br><span style="font-weight: bold; color: {color}">[{src}]</span></a></td></tr>"""

href_templ = """<a href="{href}" target="fulltext">{label}</a>"""
entry_templ = """<li>{link} [{accuarcy:.4f}]:<br/><span class="lg">{text}</span></li>"""

export_templ = """<a href="{url}">[Export Results]</a>"""

ms2color = {
    "S": "#90AA00",
    "B": "#00AA90",
    "M": "#0090AA",
    "Z": "#9000AA",
}


def urn2path(s: str) -> str:
    """
    >>> urn2path("gospel.zographensis.syntacticus.marco:4.19")
    'gospel.zographensis.syntacticus/marco.tei.xml#4_19'
    >>> urn2path("psalter.bologna.oxford.BM8:112.7")
    'psalter.bologna.oxford/BM8.tei.xml#112_7'
    >>> urn2path("psalter.sinai.syntacticus.psal-sin:10.30")
    'psalter.sinai.syntacticus/psal-sin.tei.xml#10_30'
    """
    last = s.rfind(".")
    prev = s.rfind(".", 0, last)
    return f"""{s[:prev]}/{s[prev+1:last].replace(":", ".tei.xml#")}_{s[last+1:]}"""


def path2urn(s: str) -> str:
    """
    >>> path2urn("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    'gospel.zographensis.syntacticus.marco:4.19'
    >>> path2urn("psalter.bologna.oxford/BM8.tei.xml#112_7")
    'psalter.bologna.oxford.BM8:112.7'
    >>> path2urn("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    'psalter.sinai.syntacticus.psal-sin:10.30'
    """
    return s.replace(".tei.xml#", ":").replace("_", ".").replace("/", ".")


def path2link(s: str) -> str:
    return f"{static_path}{s.replace('.tei.xml', '.html')}"


def path2url(s: str) -> str:
    return f"{base_url}{static_path}{s.replace('.tei.xml', '.html')}"


def path2loc(s: str) -> str:
    """
    >>> path2loc("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    'marco<br>4.19'
    >>> path2loc("psalter.bologna.oxford/BM8.tei.xml#112_7")
    'BM8<br>112.7'
    >>> path2loc("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    'psal-sin<br>10.30'
    """
    return s.split("/")[-1].replace(".tei.xml#", "<br>").replace("_", ".")


def path2ms(s: str) -> str:
    """
    >>> path2ms("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    'Z'
    >>> path2ms("gospel.marianus.syntacticus.marco.tei.xml#4_19")
    'M'
    >>> path2ms("psalter.bologna.oxford/BM8.tei.xml#112_7")
    'B'
    >>> path2ms("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    'S'
    """
    return s.split(".")[1][0].upper()


def build_fname(params: dict[str, str]) -> str:
    """
    >>> params = {"query": "hello", "method": "regex"}
    >>> build_fname(params)
    '/results/hello-regex-532c0ac07acee465f2585a261fefd47c.xlsx'
    >>> build_fname(params)
    '/results/hello-regex-532c0ac07acee465f2585a261fefd47c.xlsx'
    """

    m = hashlib.md5()
    for s in params.values():
        m.update(str(s).encode())

    return fname_templ.format(
        # query=quote_plus(params["query"][:20]),
        method=params["method"],
        params=m.hexdigest(),
    )


def render_from_export(fname: str) -> tuple[str, str]:

    df = pd.read_excel(fname)

    html_rows = []
    for i, row in df.iterrows():
        text = row["found"]
        addr = urn2path(row["location"])
        acc = float(row["similarity"])
        html_rows += [
            trow_templ.format(
                text=text,
                acc="1.0" if acc == 1 else f"{acc:0.3f}",
                href=path2link(addr),
                ref=path2loc(addr),
                color=ms2color[path2ms(addr)],
                src=path2ms(addr),
                urn=path2urn(addr),
            )
        ]
    html_result = table_templ.format(body="\n".join(html_rows))

    return export_templ.format(url=base_url + fname), html_result


def render_table(
    params: dict[str, str],
    data: list[tuple[str, str, float]],
) -> tuple[str, str]:
    """A list of <text, address, accuracy>. Returns path to export and HTML body.
    A precondition is that build_fname(params) does not exist."""

    data.sort(key=lambda x: x[2], reverse=True)
    if not data:
        return "Result is empty.", None

    html_rows = []
    for text, addr, acc in data:
        html_rows += [
            trow_templ.format(
                text=text,
                acc="1.0" if acc == 1 else f"{acc:.2f}".lstrip("0"),
                href=path2link(addr),
                ref=path2loc(addr),
                color=ms2color[path2ms(addr)],
                src=path2ms(addr),
                urn=path2urn(addr),
            )
        ]
    html_result = table_templ.format(body="\n".join(html_rows))

    result = [
        {
            "found": d[0],
            "similarity": f"{d[2]:0.4f}",
            "location": path2urn(d[1]),
            "url": path2url(d[1]),
        }
        for d in data
    ]
    df = pd.DataFrame(result)

    for k, v in params.items():
        df[k] = v

    col = df.pop("query")
    df.insert(0, "query", col)

    fname_result = build_fname(params)
    with pd.ExcelWriter(fname_result) as writer:
        df.to_excel(writer, index=False, sheet_name="Result")
        wb = writer.book
        font = Font(name="BukyVede")
        align = Alignment(wrap_text=True)
        ws = wb.worksheets[0]

        for cell in ws["A"]:
            cell.font = font
            cell.alignment = align
        for cell in ws["B"]:
            cell.font = font
            cell.alignment = align

        ws.column_dimensions["A"].width = 60
        ws.column_dimensions["B"].width = 60
        ws.column_dimensions["C"].width = 10
        ws.column_dimensions["D"].width = 30
        ws.column_dimensions["E"].width = 40

    return export_templ.format(url=base_url + fname_result), html_result
