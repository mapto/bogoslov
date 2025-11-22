def dummy_lemmas(_):
    return [
        "Исповѣдѧть",
        "сѧ",
        "тебѣ",
        "љѵдиѥ",
        "б҃же",
        "⁘",
        "Исповѣдѧть",
        "сѧ",
        "тебѣ",
    ]


class DummyClass:
    class pos:
        def asc(self):
            return

    pass


class DummyQuery:
    def all(self):
        return dummy_lemmas(None)

    def join(self, other, condition):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self


class DummySession:
    def query(self, entity):
        return DummyQuery()


def dummy_session():
    return DummySession()


def fixture(func):
    def wrapper(monkeypatch, *args, **kwargs):
        # import db

        # monkeypatch.setattr(db, "engine", None)
        # monkeypatch.setattr(db, "Session", dummy_session)
        # monkeypatch.setattr(db, "Base", DummyClass)

        import persist

        monkeypatch.setattr(persist, "get_lemmas", dummy_lemmas)

        return func(*args, **kwargs)

    return wrapper


@fixture
def test_stemWords():
    from app_bm25 import stemWords

    result = stemWords(
        [
            "Исповѣдѧть",
            "сѧ",
            "тебѣ",
            "љѵдиѥ",
            "б҃же",
            "⁘",
            "Исповѣдѧть",
            "сѧ",
            "тебѣ",
            "љѵдиѥ",
            "въси",
        ]
    )
    assert result == [
        "Исповѣдѧть",
        "сѧ",
        "тебѣ",
        "љѵдиѥ",
        "б҃же",
        "⁘",
        "Исповѣдѧть",
        "сѧ",
        "тебѣ",
    ]
