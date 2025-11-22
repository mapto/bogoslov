#!/usr/bin/env python3

"""BogoSlov Populate

Schema needs to be preloaded.

Usage:
  populate.py [-v | --verses] [-n | --ngrams] [-e | --embeddings] [-f | --force]
  populate.py [-v | --verses] [-n | --ngrams] [--embedding=<name>] [-f | --force]
  populate.py (-h | --help)
  populate.py --version

Options:
  -h --help            Show this screen.
  --version            Show version.
  -v --verses          Generate index for Verses.
  -n --ngrams          Generate index for Ngrams (requires index for Verses).
  -e --embeddings      Generate index for Embeddings (requires index for Verses).
  --embedding=<name>   Generate index for Embeddings only for model <name> (requires index for Verses).
  -f --force           Force Embedding regeneration even if it exists already.

"""

from lxml import etree
from glob import glob

from tqdm import tqdm
from docopt import docopt
from sentence_transformers import SentenceTransformer
from sqlalchemy import delete  # type: ignore

from model import Verse, Ngram, Embedding

from settings import ns, unit, strans_models as models, ng_min, ng_max, ng_default
from db import engine, Session, Base

src = "/corpora/*/*.tei.xml"


def persist_verse(s: Session, fname: str):
    print(fname)
    corpus = fname.split("/")[-2]
    ch = fname.split("/")[-1]
    root = etree.parse(fname)
    result = root.xpath(f"//tei:{unit}", namespaces=ns)
    data = []
    for e in tqdm(result):
        eid = e.get("id")
        tcontents = e.xpath(
            f"""//tei:{unit}[@id='{eid}']//tei:w/text()""", namespaces=ns
        )
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
                pos=i,
            )
        ]
    s.add_all(ngrams)
    s.commit()


def persist_embedding(m: str, force=False):
    model = SentenceTransformer(m)
    vectors = []
    q = s.query(Verse)
    cnt = q.count()
    preexistent = s.query(Embedding).filter(Embedding.model == m).count()
    if cnt == preexistent and not force:
        print(f"Model {m} already loaded.")
        return
    if preexistent > 0:
        print(f"Cleaning up partially preloaded model {m}.")
        s.execute(delete(Embedding).where(Embedding.model == m))
    for v in tqdm(q.all(), total=cnt):
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


if __name__ == "__main__":
    args = docopt(__doc__, version="BogoSlov Populate 1.0")
    # print(args)

    Base.metadata.create_all(engine)
    s = Session()

    if args["--verses"]:
        print("# Indexing Verses...")
        for fname in glob(src):
            persist_verse(s, fname)

    if args["--ngrams"]:
        files = list(
            s.query(Verse.path, Verse.filename)
            .group_by(Verse.path, Verse.filename)
            .all()
        )
        # print(files)
        for path, filename in files:
            print(f"# Indexing N-grams: {path}/{filename}...")
            q = s.query(Verse).filter(Verse.path == path, Verse.filename == filename)
            for v in tqdm(q.all(), total=q.count()):
                for n in range(ng_min, ng_max + 1):
                    persist_ngram(s, v, n)

    if args["--embeddings"]:
        for m in models:
            print(f"# Indexing model: {m}...")
            persist_embedding(m, force=args["--force"])

    elif args["--embedding"]:
        m = args["--embedding"]
        if m not in models:
            print(f"Available models: {models}")
        else:
            print(f"# Indexing model: {m}...")
            try:
                persist_embedding(m, force=args["--force"])
            except ValueError as ve:
                print(repr(ve))
