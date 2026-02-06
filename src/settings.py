import importlib
import os
import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

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
port = int(os.environ.get("DEPLOY_PORT", "8780"))
base_url = f"http://{host}:{port}"

ns = {"tei": "http://www.tei-c.org/ns/1.0"}
unit = "lg"

# usability
threshold_lcs = config["threshold_lcs"]
threshold_ngram = config["threshold_ngram"]
threshold_strans = config["threshold_strans"]
threshold_bm25 = config["threshold_bm25"]

# actually lemmatizer
stemmer = config["stemmer"]


# ngrams, see app_ngram.py#39
ng_min = 1
ng_default = 3
ng_max = 3

debug = config["debug"]
