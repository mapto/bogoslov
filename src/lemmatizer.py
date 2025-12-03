from settings import stemmer

from udpipeclient import udpipe_sent_lemmatize


def tokenizer(sent: str)-> list[str]:
    return sent.split()

sent_stemmers = {
    "dummy": lambda x: [(t, t) for t in tokenizer(x) if t.strip()],
    "udpipe": udpipe_sent_lemmatize,
}

try:
    from stanzaclient import stanza_sent_lemmatize
    sent_stemmers["stanza"] = stanza_sent_lemmatize
except ImportError:
    pass

lemmatizer = sent_stemmers[stemmer]