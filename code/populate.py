#!/usr/bin/env python3

from lxml import etree
from glob import glob
from tqdm import tqdm

from db import Session, Base, engine
from model import Verse, Ngram

Base.metadata.create_all(engine)

s = Session()

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

for v in s.query(Verse).all():
    print(f"{v.path}.{v.filename}.{v.address}")
    ngrams = []
    for n in tqdm(range(2, 11)):
        tokens = [l for l in v.text.split(" ") if l]
        lemmas = [l for l in v.lemmas.split(",") if l]
        for i in range(len(lemmas) - n + 1):
            ng = tuple(lemmas[i : i + n])
            if len(tokens) >= i + n:
                text = " ".join(tokens[i : i + n])
            elif len(tokens) > i:
                text = " ".join(tokens[i:])
            else:
                text = ""
            ngrams += [
                Ngram(
                    n=n,
                    path=v.path,
                    filename=v.filename,
                    address=v.address,
                    lemmas=",".join(lemmas[i : i + n]),
                    text=text,
                )
            ]
    s.add_all(ngrams)
    s.commit()
