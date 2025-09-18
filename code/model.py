#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from sqlalchemy import Column, Computed, ForeignKey  # type: ignore
from sqlalchemy import Integer, String, DateTime  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from sqlalchemy.orm import relationship, mapped_column
from pgvector.sqlalchemy import Vector

from db import Base, Session, engine

# vdims = 384
vdims = 768


class Verse(Base):
    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String)
    filename = Column(String)
    address = Column(String)
    text = Column(String, default="")
    lemmas = Column(String, default="")

    def __str__(self):
        return str({c.name: getattr(self, c.name) for c in self.__table__.columns})


class Ngram(Base):
    """Used only by the n-gram app, pos is used for uniqueness validation only"""

    __tablename__ = "ngrams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lemmas = Column(String)
    text = Column(String)
    n = Column(Integer)
    pos = Column(Integer)

    verse_id = Column(Integer, ForeignKey("verses.id"))

    def __str__(self):
        return str({c.name: getattr(self, c.name) for c in self.__table__.columns})


class Embedding(Base):
    """Used only by the strans app"""

    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String)
    vector = mapped_column(Vector(vdims))

    verse_id = Column(Integer, ForeignKey("verses.id"))

    def __str__(self):
        return str({c.name: getattr(self, c.name) for c in self.__table__.columns})


def init():
    # print("Creating database at: %s" % DATABASE_URL)
    Base.metadata.create_all(engine)

    s = Session()


def preview():
    from eralchemy2 import render_er

    render_er(Base, "model.png")


if __name__ == "__main__":
    init()
    # try:
    preview()
    # except:
    #    pass
