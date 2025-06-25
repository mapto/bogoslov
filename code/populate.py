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

from db import Base
from model import Verse, Ngram, Embedding

Base.metadata.create_all(engine)

s = Session()
# s.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

src = "../corpora/*/*.tei.xml"

# s.delete(s.query(Verse).all())

# for fname in glob(src):
#     print(fname)
#     corpus = fname.split("/")[-2]
#     ch = fname.split("/")[-1]
#     root = etree.parse(fname)
#     result = root.xpath(f"//tei:{unit}", namespaces=ns)
#     data = []
#     for e in tqdm(result):
#         eid = e.get("id")
#         tcontents = e.xpath(f"""//tei:{unit}[@id='{eid}']//tei:w/text()""", namespaces=ns)
#         lcontents = e.xpath(
#             f"""//tei:{unit}[@id='{eid}']//tei:w/@lemma""", namespaces=ns
#         )
#         if not tcontents or (len(tcontents) == 1 and not tcontents[0].strip()):
#             continue
#         data += [
#             Verse(
#                 path=corpus,
#                 filename=ch,
#                 address=eid,
#                 text=" ".join(tcontents),
#                 lemmas=",".join(lcontents),
#             )
#         ]
#     s.add_all(data)
#     s.commit()

# for v in tqdm(s.query(Verse).all()):
#     # print(f"{v.path}.{v.filename}.{v.address}")
#     ngrams = []
#     for n in range(2, 11):
#         tokens = [l for l in v.text.split(" ") if l]
#         lemmas = [l for l in v.lemmas.split(",") if l]
#         for i in range(len(lemmas) - n + 1):
#             ng = tuple(lemmas[i : i + n])
#             # TODO: handle better lemmatization mismatches
#             if len(tokens) >= i + n:
#                 text = " ".join(tokens[i : i + n])
#             elif len(tokens) > i:
#                 text = " ".join(tokens[i:])
#             else:
#                 text = ""
#             ngrams += [
#                 Ngram(
#                     n=n,
#                     lemmas=",".join(lemmas[i : i + n]),
#                     text=text,
#                     verse_id=v.id,
#                 )
#             ]
#     s.add_all(ngrams)
#     s.commit()

models = [
    # "uaritm/multilingual_en_uk_pl_ru",  # 768
    # "cointegrated/rubert-tiny2", # 312
    "pouxie/LaBSE-en-ru-bviolet",
    "Den4ikAI/sbert_large_mt_ru_retriever",
    "siberian-lang-lab/evenki-russian-parallel-corpora",
    "Diiiann/ru_oss",
    "DiTy/bi-encoder-russian-msmarco",
]

for m in tqdm(models):
    # m = "uaritm/multilingual_en_uk_pl_ru"
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
