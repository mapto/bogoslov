import importlib
import os
lang = os.environ.get('LANG_CORPUS', 'chu')
langmod = importlib.import_module(f"lang_{lang}")

print(f"Loading for LANG_CORPUS={lang}...")

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


ms2color = langmod.ms2color
ms2source = langmod.ms2source
udpipe_model = langmod.udpipe_model
strans_models = langmod.strans_models
