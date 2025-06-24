import spacy_stanza


nlp = spacy_stanza.load_pipeline("xx", lang="cu", use_gpu=False)


def stanza_lemmatize(word, sent):
    if not sent:
        sent = word
    doc = nlp(sent)
    for token in doc:
        if token.text == word:
            return token.lemma_


def stanza_sent_lemmatize(sent):
    doc = nlp(sent)
    return [(token.text, token.lemma_) for token in doc]
