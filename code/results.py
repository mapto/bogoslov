from settings import static_path

pfa_templ = "{path}/{fname}#{addr}"

href_templ = """<a href="{href}" target="fulltext">{label}</a>"""
entry_templ = """<li>{link} [{accuarcy:.4f}]:<br/><span class="lg">{text}</span></li>"""

def path2urn(s: str) -> str:
    return s.replace(".tei.xml#", ":").replace("_", ".").replace("/", ".")

def path2link(s: str) -> str:
    return f"{static_path}{s.replace('.tei.xml', '.html')}"



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
