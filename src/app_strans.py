#!/usr/bin/env python3

from pathlib import Path
import random
import logging

import gradio as gr

from settings import threshold_strans
from persist import find_embeddings, get_strans_models, get_sources
from results import render_table, render_from_export, build_fname
from results import pfa_templ, sources2code
from settings import lang, strans_models, examples

logger = logging.getLogger(__name__)


def find(sources: list[str], fulltext: str, model: str) -> list[tuple[str, str, float]]:
    """
    The function that performs the search.
    Takes the query string as parameter and the model identifier on HuggingFace.
    """
    logger.debug(f"Starting {__name__}/{model}")
    response = find_embeddings(model, fulltext, threshold_strans, sources)
    result = [
        (r[0], pfa_templ.format(path=r[1], fname=r[2], addr=r[3]), r[4])
        for r in response
    ]

    return result


def wrapper(sources: list[str], fulltext: str, model: str) -> tuple[str, str]:
    params = {
        "query": fulltext,
        "method": "strans",
        "model": model,
        "sources": sources2code(sources),
    }
    fname_result = build_fname(params)
    if Path(fname_result).exists():
        return render_from_export(fname_result)

    result = find(sources, fulltext, model)
    output = render_table(params, result)

    return output


def interface() -> gr.Interface:
    models = get_strans_models()
    sources = get_sources()

    app = gr.Interface(
        fn=wrapper,
        description="""<h1>Sentence Transformers</h1><small>See <a href="https://www.sbert.net">sbert.net</a> and <a href="https://github.com/mapto/bogoslov/blob/main/code/app_strans.py#L17">implementation</a>.</small>""",
        inputs=[
            gr.CheckboxGroup(sources, value=sources, label="Sources"),
            gr.Textbox(random.choice(examples), lines=5, label="Search"),
            gr.Dropdown(models, value=strans_models[0], label="Model"),
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
        server_port=7861, server_name="0.0.0.0", show_api=False, root_path="/strans"
    )
