import importlib
import os

lang = os.environ.get("LANG_CORPUS", "chu")
lang = os.environ.get("LANG_CORPUS", "chu")
langmod = importlib.import_module(f"lang_{lang}")

print(f"Loading for LANG_CORPUS={lang}...")
ms2color = langmod.ms2color
ms2source = langmod.ms2source
udpipe_model = langmod.udpipe_model
strans_models = langmod.strans_models
examples = langmod.examples

# DATABASE_URL = "sqlite+pysqlite:///:memory:"
# DATABASE_URL = "postgresql://bogoslov:xxxxxx@localhost:5732/bogoslov

DATABASE_URL = "postgresql://bogoslov:xxxxxx@db:5432/bogoslov"

static_path = "/corpora/"
host = os.environ.get("DEPLOY_HOST", "127.0.0.1")
port = os.environ.get("DEPLOY_PORT", "8780")
base_url = f"http://{host}:{port}"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

# usability
# threshold_lcs = 0.3
# threshold_ngram = 0.3
# threshold_strans = 0.75

# evaluation
threshold_lcs = 0.01
threshold_ngram = 0.01
threshold_strans = 0.1

spacy_models = []

# ngrams, see app_ngram.py#39
ng_min = 1
ng_default = 3
ng_max = 3

# debug = True
debug = False
