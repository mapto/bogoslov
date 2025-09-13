from pathlib import Path

import pandas as pd

from settings import static_path, base_url

pfa_templ = "{path}/{fname}#{addr}"

table_templ = """<table class="results">{body}</table>"""
trow_templ = """<tr><td class="quote">{text}</td><td class="info"><span title="accuracy" style="font-size: large; opacity: {acc}">{acc}</span><br><a href="{href}" title="{urn}">{ref}<br><span style="font-weight: bold; color: {color}">[{src}]</span></a></td></tr>"""

href_templ = """<a href="{href}" target="fulltext">{label}</a>"""
entry_templ = """<li>{link} [{accuarcy:.4f}]:<br/><span class="lg">{text}</span></li>"""

ms2color = {
    "S": "#90AA00",
    "B": "#00AA90",
    "M": "#0090AA",
    "Z": "#9000AA",
}


def path2urn(s: str) -> str:
    """
    >>> path2urn("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    "gospel.zographensis.syntacticus.marco:4.19"
    >>> path2urn("psalter.bologna.oxford/BM8.tei.xml#112_7")
    "psalter.bologna.oxford.BM8:112.7"
    >>> path2urn("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    "psalter.sinai.syntacticus.psal-sin:10.30"
    """
    return s.replace(".tei.xml#", ":").replace("_", ".").replace("/", ".")


def path2link(s: str) -> str:
    return f"{static_path}{s.replace('.tei.xml', '.html')}"


def path2url(s: str) -> str:
    return f"{base_url}{static_path}{s.replace('.tei.xml', '.html')}"

def path2loc(s: str) -> str:
    """
    >>> path2urn("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    "marco<br>4.19"
    >>> path2urn("psalter.bologna.oxford/BM8.tei.xml#112_7")
    "BM8<br>112.7"
    >>> path2urn("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    "psal-sin<br>10.30"
    """
    return s.split("/")[-1].replace(".tei.xml#", "<br>").replace("_", ".")


def path2ms(s: str) -> str:
    """
    >>> path2ms("gospel.zographensis.syntacticus/marco.tei.xml#4_19")
    "Z"
    >>> path2ms("gospel.marianus.syntacticus.marco.tei.xml#4_19")
    "M"
    >>> path2ms("psalter.bologna.oxford/BM8.tei.xml#112_7")
    "B"
    >>> path2ms("psalter.sinai.syntacticus/psal-sin.tei.xml#10_30")
    "S"
    """
    return s.split(".")[1][0].upper()


def render(data: list[tuple[str, str, float]]) -> str:
    """a list of <text, address, accuracy>"""

    data.sort(key=lambda x: x[2], reverse=True)
    if not data:
        return "Result is empty."
    result = []
    # print(data)
    for text, address, accuarcy in data:
        link = href_templ.format(
            label=path2urn(address),
            href=path2link(address),
        )
        result += [entry_templ.format(link=link, accuarcy=accuarcy, text=text)]
    return "\n".join(result)


def render_table(
    params: dict[str, str],
    data: list[tuple[str, str, float]],
) -> tuple[str, str]:
    """a list of <text, address, accuracy>. Returns path to export and HTML body."""

    data.sort(key=lambda x: x[2], reverse=True)
    if not data:
        return "Result is empty.", None

    html_rows = []
    for text, addr, acc in data:
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

    result = [
        {
            "found": d[0],
            "location": path2urn(d[1]),
            "url": path2url(d[1]),
            "similarity": d[2],
        }
        for d in data
    ]
    df = pd.DataFrame(result)

    for k, v in params.items():
        df[k] = v

    fname_result = f"/results/{hash(tuple(params.values()))}.xlsx"
    if not Path(fname_result).exists():
        with pd.ExcelWriter(fname_result, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Result")
            wb = writer.book
            text_format = wb.add_format({
                'text_wrap': True,
                'font_name':'BukyVede',
                })
            ws = wb.get_worksheet_by_name("Result")
            ws.set_column(0,0, 60, text_format)
            ws.set_column(4,4, 40, text_format)
            ws.set_column(1,2, 20)
            # ws.set_column(1,2, 10)

    return f'<a href="{fname_result}">Download</a>', html_result
    # return fname_result, html_result
