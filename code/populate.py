#!/usr/bin/env python3

from lxml import etree
from glob import glob
from tqdm import tqdm

from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

DATABASE_URL = "postgresql://bogoslov:xxxxxx@localhost:5732/bogoslov"
engine = create_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

src = "../corpora/*/*.tei.xml"

Base.metadata.create_all(engine)
s = Session()

def persist_verse(s: Session, fname: str):
    print(fname)
    corpus = fname.split("/")[-2]
    ch = fname.split("/")[-1]
    root = etree.parse(fname)
    result = root.xpath(f"//tei:{unit}", namespaces=ns)
    data = []
    for e in tqdm(result):
        eid = e.get("id")
        tcontents = e.xpath(f"""//tei:{unit}[@id='{eid}']//tei:w/text()""", namespaces=ns)
        lcontents = e.xpath(
            f"""//tei:{unit}[@id='{eid}']//tei:w/@lemma""", namespaces=ns
        )
        if not tcontents or (len(tcontents) == 1 and not tcontents[0].strip()):
            continue
        data += [
            Verse(
                path=corpus,
                filename=ch,
                address=eid,
                text=" ".join(tcontents),
                lemmas=",".join(lcontents),
            )
        ]
    s.add_all(data)
    s.commit()

def persist_ngram(s, verse: str, n: int):
    ngrams = []
    tokens = [l for l in v.text.split(" ") if l]
    lemmas = [l for l in v.lemmas.split(",") if l]
    for i in range(len(lemmas) - n + 1):
        ng = tuple(lemmas[i : i + n])
        # TODO: handle better lemmatization mismatches
        if len(tokens) >= i + n:
            text = " ".join(tokens[i : i + n])
        elif len(tokens) > i:
            text = " ".join(tokens[i:])
        else:
            text = ""
        ngrams += [
            Ngram(
                n=n,
                lemmas=",".join(lemmas[i : i + n]),
                text=text,
                verse_id=v.id,
            )
        ]
    s.add_all(ngrams)
    s.commit()

def persist_embedding(m: str):
    model = SentenceTransformer(m)
    vectors = []
    for v in s.query(Verse).all():
        primary = model.encode(v.text)
        vectors += [
            Embedding(
                model=m,
                vector=primary,
                verse_id=v.id,
            )
        ]
    s.add_all(vectors)
    s.commit()


models = [
    "uaritm/multilingual_en_uk_pl_ru",  # 768
    # "cointegrated/rubert-tiny2", # 312
    "pouxie/LaBSE-en-ru-bviolet",  # 768
    # "Den4ikAI/sbert_large_mt_ru_retriever",  # 1024
    "siberian-lang-lab/evenki-russian-parallel-corpora",  # 768
    "Diiiann/ru_oss",  # 768
    "DiTy/bi-encoder-russian-msmarco",  # 768
]

if __name__ == "__main__":
    for fname in glob(src):
        persist_verse(s, fname)

    for v in tqdm(s.query(Verse).all()):
        for n in range(2, 11):
            persist_ngram(s, v, n)

    # download models
    for m in models:
        SentenceTransformer(m)

    for m in tqdm(models):
        persist_embedding(m)

