from sqlalchemy import select
from sentence_transformers import SentenceTransformer

from db import Session, Base, engine
from model import Verse, Ngram, Embedding


def find_ngram(
    n: int, lngram: str, estart: int, eend: int, etext: str
) -> list[tuple[str, str, str]]:
    s = Session()
    result = s.query(Ngram).filter(Ngram.n == n, Ngram.lemmas == lngram).all()
    return [(r.path, r.filename, r.address) for r in result]

def get_models() -> list[str]:
    s = Session()
    return [r.model for r in s.query(Embedding.model).group_by(Embedding.model).all()]


def find_embeddings(model_name: str, text: str) -> list[str]:
    s = Session()
    model = SentenceTransformer(model_name)
    quote = model.encode(text)

    # TODO: filter by model
    # return s.scalars(select(Embedding).order_by(Embedding.vector.cosine_distance(quote)).limit(10))
    # return select(Embedding).order_by(Embedding.vector.cosine_distance(quote)).limit(10)
    result = (
        s.query(Embedding, Verse)
        .filter(Embedding.model == model_name)
        .filter(Embedding.verse_id == Verse.id)
        .order_by(Embedding.vector.cosine_distance(quote))
        .limit(10)
    )
    return [(f"{r[1].path}/{r[1].filename}#{r[1].address}", r[1].text) for r in result]


# result = find_embeddings(
#     "uaritm/multilingual_en_uk_pl_ru", "Блаженъ мѫжъ иже не иде на съвѣть нечъстивъїхъ"
# )
# print(result)
