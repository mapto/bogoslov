from settings import static_path

pfa_templ = "{path}/{fname}#{addr}"

href_templ = """<a href="{href}" target="fulltext">{label}</a>"""
entry_templ = "<li>{link} [{accuarcy:.4f}]:<br/>{text}</li>"


def render(data: list[tuple[str, str, float]]) -> str:
    """a list of <text, address, accuracy>"""

    data.sort(key=lambda x: x[2], reverse=True)
    if not data:
        return "Result is empty."
    result = []
    # print(data)
    for text, address, accuarcy in data:
        link = href_templ.format(
            label=address.replace(".tei.xml#", ":").replace(".", ":").replace("_", "."),
            href=f"{static_path}{address.replace('.tei.xml', '.html')}",
        )
        result += [entry_templ.format(link=link, accuarcy=accuarcy, text=text)]
    return "\n".join(result)
