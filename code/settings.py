# DATABASE_URL = "sqlite+pysqlite:///:memory:"
# DATABASE_URL = "postgresql://bogoslov:xxxxxx@localhost:5732/bogoslov"
DATABASE_URL = "postgresql://bogoslov:xxxxxx@db:5432/bogoslov"

static_path = "/corpora/"
base_url = "http://157.180.18.192:8780"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

threshold = 0.5

spacy_models = []

max_ngram = 5

# debug = True
debug = False

ms2color = {
    "S": "#90AA00",
    "B": "#00AA90",
    "M": "#0090AA",
    "Z": "#9000AA",
}

ms2source = {
    "S": "psalter.sinai.syntacticus",
    "B": "psalter.bologna.oxford",
    "M": "gospel.marianus.syntacticus",
    "Z": "gospel.zographensis.syntacticus",
}
