from sqlalchemy import select
from sentence_transformers import SentenceTransformer

from settings import threshold
from db import Session, Base, engine
from model import Verse, Ngram, Embedding

strans_models = None


def get_verse_text(path, filename, address) -> str:
    s = Session()
    result = (
        s.query(Verse.text)
        .filter(Verse.path == path)
        .filter(Verse.filename == filename)
        .filter(Verse.address == address)
        .first()
    )
    return result[0]


def get_texts() -> list[tuple[str, str, str, str]]:
    s = Session()

    result = s.query(Verse).all()
    return [(r.path, r.filename, r.address, r.text) for r in result]


def find_regex(pattern: str, operator: str) -> list[tuple[str, str, str]]:
    s = Session()
    result = (
        s.query(Verse)
        .filter(Verse.text.op(operator, is_comparison=True)(pattern))
        .all()
    )
    return [(r.path, r.filename, r.address) for r in result]


def find_ngram(
    n: int, lngram: str, estart: int, eend: int, etext: str
) -> list[tuple[str, str, str]]:
    s = Session()
    result = (
        s.query(Ngram, Verse)
        .filter(Ngram.n == n, Ngram.lemmas == lngram)
        .filter(Ngram.verse_id == Verse.id)
        .all()
    )
    return [(r[1].path, r[1].filename, r[1].address) for r in result]


def get_strans_models() -> list[str]:
    s = Session()

    if "available_models" not in globals():
        global available_models
        available_models = [
            r.model for r in s.query(Embedding.model).group_by(Embedding.model).all()
        ]
        # strans_models = {m: SentenceTransformer(m) for m in available_models}

    return available_models


def find_embeddings(
    model_name: str, text: str, dist_threshold: float = 0.2
) -> list[tuple[str, str, float]]:
    s = Session()
    model = SentenceTransformer(model_name)
    quote = model.encode(text)

    result = (
        s.query(Embedding, Verse, Embedding.vector.cosine_distance(quote))
        .filter(Embedding.model == model_name)
        .filter(Embedding.verse_id == Verse.id)
        .filter(Embedding.vector.cosine_distance(quote) <= dist_threshold)
        .all()
    )
    return [
        (r[1].text, r[1].path, r[1].filename, r[1].address, 1 - r[2]) for r in result
    ]


# result = find_embeddings(
#     "uaritm/multilingual_en_uk_pl_ru", "Блаженъ мѫжъ иже не иде на съвѣть нечъстивъїхъ"
# )
# print(result)
