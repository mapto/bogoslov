def dummy_texts(_):
    return [("/", "none.txt", "1", "Въсѣ землѣ да поклоні-т-і сѩ і поетъ тебѣ:")]


def dummy_sources():
    return []


class DummyClass:
    pass


class DummyQuery:
    def all(self):
        return dummy_texts(None)


class DummySession:
    def query(self, entity):
        return DummyQuery()


def dummy_session():
    return DummySession()


def fixture(func):
    def wrapper(monkeypatch, *args, **kwargs):
        import db

        monkeypatch.setattr(db, "engine", None)
        monkeypatch.setattr(db, "Session", dummy_session)
        monkeypatch.setattr(db, "Base", DummyClass)

        import persist

        monkeypatch.setattr(persist, "get_sources", dummy_sources)
        monkeypatch.setattr(persist, "get_texts", dummy_texts)

        import results

        monkeypatch.setattr(results, "render_table", lambda params, res: res)

        return func(*args, **kwargs)

    return wrapper


@fixture
def test_find_case():
    from app_lcs import find

    result = find([], "въса землꙗ да поклонит ти се и поеть тебе", match_case=True)
    assert result == [
        (
            "ъсѣ землѣ да поклоні-т-і сѩ і поетъ теб",
            "//none.txt#1",
            0.75,
        )
    ]


@fixture
def test_find_nocase():
    from app_lcs import find

    result = find([], "въса землꙗ да поклонит ти се и поеть тебе", match_case=False)
    assert result == [
        (
            "въсѣ землѣ да поклоні-т-і сѩ і поетъ теб",
            "//none.txt#1",
            0.7654320987654321,
        )
    ]
