#!/usr/bin/env python3
"""The BogoSlov API, see 4euplus.eu/4EU-1150.html and https://ceur-ws.org/Vol-3937/short8.pdf"""

from typing import Annotated, Callable
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import gradio as gr

from settings import ms2source, examples, port, lang
from persist import get_strans_models
from results import render_excel, render_html, render_json

import app_regex
import app_lcs
import app_ngram
import app_strans
import app_bm25

import logging

logging.basicConfig(level=logging.DEBUG)

all_sources = "".join(ms2source.keys())
strans_models = {m.split("/")[1]: m for m in get_strans_models()}
mime_xlsx = "application/vnd.ms-excel"
headers_xlsx = {"content-type": mime_xlsx}

algos: dict[str, Callable[[list[str], str], list[tuple[str, str, float]]]] = {
    "regex": app_regex.find,
    "lcs": app_lcs.find,
    "ngram": app_ngram.find,
    "bm25": app_bm25.find,
}


class SearchParams(BaseModel):
    sources: str = Field(
        default=all_sources,
        description="Concatenated initials of sources to search in, see /settings for initial interpretations.",
        examples=[all_sources],
    )
    fulltext: str = Field(
        description="The text to query for quotations.", examples=examples
    )
    result_format: str = Field(
        default="html",
        description="File format of the output.",
        examples=["html", "json", "xlsx"],
    )


app = FastAPI(
    title=f"BogoSlov ({lang})",
    description=__doc__,
    # docs_url="/",
    version="0.1.0",
)


@app.get("/api/{algo}")
async def query(algo: str, search: Annotated[SearchParams, Query()]):
    params = {
        "query": search.fulltext,
        "method": algo,
        "sources": search.sources,
    }

    sources = [ms2source[s] for s in search.sources]

    if algo in algos:
        result = algos[algo](sources, search.fulltext)
    elif algo in strans_models.keys():
        result = app_strans.find(sources, search.fulltext, model=strans_models[algo])
    else:
        raise HTTPException(404, detail="Undefined algorithm")

    if not result:
        raise HTTPException(204, detail="No results")

    if search.result_format == "html":
        return HTMLResponse(content=render_html(result))
    if search.result_format == "json":
        return JSONResponse(content=render_json(result))
    if search.result_format == "xlsx":
        fname = render_excel(params, result)
        fpath = f"/results/{fname}"
        if Path(fpath).exists():
            return FileResponse(
                fpath,
                status_code=201,
                filename=fname,
                media_type=mime_xlsx,
                headers=headers_xlsx,
            )
        else:
            raise HTTPException(500, detail="File not exported.")


gr.mount_gradio_app(app, app_regex.interface(), path="/regex")
gr.mount_gradio_app(app, app_lcs.interface(), path="/lcs")
gr.mount_gradio_app(app, app_ngram.interface(), path="/ngram")
gr.mount_gradio_app(app, app_strans.interface(), path="/strans")
gr.mount_gradio_app(app, app_bm25.interface(), path="/bm25")


@app.get("/settings")
async def settings():
    """Returns the language of the installation. Also serves as healthcheck"""
    return JSONResponse(
        content={
            "version": app.version,
            "language": lang,
            "sources": ms2source,
            "sentence_transformer_models": {
                m.split("/")[1]: m for m in strans_models.values()
            },
            "explicit_algorithms": list(algos.keys()),
        },
        status_code=200,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
