import stanza

stanza.download("cu")
nlp = stanza.Pipeline("cu", use_gpu=False)


def stanza_lemmatize(word, sent):
    if not sent:
        sent = word
    doc = nlp(sent)
    for sent in doc.sentences:
        for token in sent.words:
            if token.text == word:
                return token.lemma_


def stanza_sent_lemmatize(sent):
    doc = nlp(sent)
    return [(token.text, token.lemma) for sent in doc.sentences for token in sent.words]
