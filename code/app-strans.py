#!/usr/bin/env python3

from pathlib import Path

import gradio as gr

from settings import threshold
from persist import find_embeddings, get_strans_models, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code


def find(sources: list[str], fulltext: str, m: str) -> str:
    """
    The function that performs the search.
    Takes the query string as parameter and the model identifier on HuggingFace.
    """
    params = {
        "query": fulltext,
        "method": "strans",
        "model": m,
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return render_from_export(fname_result)

    response = find_embeddings(m, fulltext, 1 - threshold, sources)
    result = [
        (r[0], pfa_templ.format(path=r[1], fname=r[2], addr=r[3]), r[4])
        for r in response
    ]

    output = render_table(params, result)

    return output


def interface() -> gr.Interface:
    models = get_strans_models()
    sources = get_sources()

    app = gr.Interface(
        fn=find,
        description="""<h1>Sentence Transformers</h1><small>See <a href="https://www.sbert.net">sbert.net</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app-strans.py#L17">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox("Не осѫждаите да не осѫждени бѫдете", lines=5, label="Search"),
            gr.Dropdown(models, value="uaritm/multilingual_en_uk_pl_ru", label="Model"),
        ],
        outputs=[
            gr.HTML(label="Download"),
            gr.HTML(label="Results"),
        ],
        css_paths="/static/ocs.css",
    )

    return app


if __name__ == "__main__":
    app = interface()
    app.launch(
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/strans"
    )
