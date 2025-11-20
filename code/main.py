#!/usr/bin/env python3
"""The BogoSlov API, see 4euplus.eu/4EU-1150.html and https://ceur-ws.org/Vol-3937/short8.pdf"""

from typing import Annotated
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import importlib
from pathlib import Path

import gradio as gr

from settings import ms2source
from util import link2fname

regex = importlib.import_module("app-regex")
lcs = importlib.import_module("app-lcs")
ngram = importlib.import_module("app-ngram")
strans = importlib.import_module("app-strans")
bm25 = importlib.import_module("app-bm25")

all_sources = "".join(ms2source.keys())

# mime_xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
mime_xlsx = "application/vnd.ms-excel"
headers_xlsx = {"content-type": mime_xlsx}
#


class SearchParams(BaseModel):
    sources: str = Field(default=all_sources, examples=[all_sources])
    fulltext: str = Field(
        examples=[
            "Не осѫждаите да не осѫждени бѫдете",
            "въса землꙗ да поклонит ти се и поеть тебе",
            "Приде же въ градъ самарьскъ",
        ]
    )
    match_case: bool | None = Field(default=None)
    whole_words: bool | None = Field(default=None)
    n: int | None = Field(default=None, examples=[4])
    model: str | None = Field(
        default=None, examples=["sentence-transformers/LaBSE"]
    )


app = FastAPI(
    title="BogoSlov",
    description=__doc__,
    # docs_url="/",
    version="0.0.1",
)


@app.get("/api/regex")
async def query_regex(search: Annotated[SearchParams, Query()]):
    """Considers match_case and whole_words"""
    sources = [ms2source[s] for s in search.sources]
    regex_str, link, html = regex.find(
        sources, search.fulltext, search.match_case, search.whole_words
    )
    if "href" not in link:
        raise HTTPException(204, detail=link)

    fname = link2fname(link)
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


@app.get("/api/ngram")
async def query_ngram(search: Annotated[SearchParams, Query()]):
    """Considers only N"""
    n = search.n if search.n else 4
    sources = [ms2source[s] for s in search.sources]
    ltext, link, html = ngram.find(sources, search.fulltext, n)
    if "href" not in link:
        raise HTTPException(204, detail=link)

    fname = link2fname(link)
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


@app.get("/api/lcs")
async def query_lcs(search: Annotated[SearchParams, Query()]):
    """No optional parameters"""
    sources = [ms2source[s] for s in search.sources]
    link, html = lcs.find(sources, search.fulltext)
    if "href" not in link:
        raise HTTPException(204, detail=link)

    fname = link2fname(link)
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


@app.get("/api/strans")
async def query_strans(search: Annotated[SearchParams, Query()]):
    """Considers only model name"""
    model = search.model if search.model else "sentence-transformers/LaBSE"
    sources = [ms2source[s] for s in search.sources]
    link, html = strans.find(sources, search.fulltext, model)
    if "href" not in link:
        raise HTTPException(204, detail=link)

    fname = link2fname(link)
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


@app.get("/api/bm25")
async def query_bm25(search: Annotated[SearchParams, Query()]):
    """No optional parameters"""
    sources = [ms2source[s] for s in search.sources]
    link, html = bm25.find(sources, search.fulltext)
    if "href" not in link:
        raise HTTPException(204, detail=link)

    fname = link2fname(link)
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


app = gr.mount_gradio_app(app, regex.interface(), path="/regex")
app = gr.mount_gradio_app(app, lcs.interface(), path="/lcs")
app = gr.mount_gradio_app(app, ngram.interface(), path="/ngram")
app = gr.mount_gradio_app(app, strans.interface(), path="/strans")
app = gr.mount_gradio_app(app, bm25.interface(), path="/bm25")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
