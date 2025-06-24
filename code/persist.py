from db import Session, Base, engine
from model import Verse, Ngram


def find_ngram(
    n: int, lngram: str, estart: int, eend: int, etext: str
) -> list[tuple[str, str, str]]:
    s = Session()
    result = s.query(Ngram).filter(Ngram.n == n, Ngram.lemmas == lngram).all()
    return [(r.path, r.filename, r.address) for r in result]
