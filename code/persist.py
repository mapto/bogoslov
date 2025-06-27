from sqlalchemy import select
from sentence_transformers import SentenceTransformer

from settings import threshold
from db import Session, Base, engine
from model import Verse, Ngram, Embedding

models = None


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


def get_models() -> list[str]:
    global models

    s = Session()

    if not models:
        available_models = [
            r.model for r in s.query(Embedding.model).group_by(Embedding.model).all()
        ]
        models = {m: SentenceTransformer(m) for m in available_models}

    return list(models.keys())


def find_embeddings(model_name: str, text: str, distance_threshold: float = .8) -> list[tuple[str, str, float]]:
    s = Session()
    model = models[model_name]
    quote = model.encode(text)

    # TODO: filter by model
    # return s.scalars(select(Embedding).order_by(Embedding.vector.cosine_distance(quote)).limit(10))
    # return select(Embedding).order_by(Embedding.vector.cosine_distance(quote)).limit(10)
    result = (
        s.query(Embedding, Verse, Embedding.vector.cosine_distance(quote))
        .filter(Embedding.model == model_name)
        .filter(Embedding.verse_id == Verse.id)
        .filter(Embedding.vector.cosine_distance(quote) <= distance_threshold)
        .all()
    )
    return [
        (r[1].text, r[1].path, r[1].filename, r[1].address, 1 - r[2]) for r in result
    ]


# result = find_embeddings(
#     "uaritm/multilingual_en_uk_pl_ru", "Блаженъ мѫжъ иже не иде на съвѣть нечъстивъїхъ"
# )
# print(result)
