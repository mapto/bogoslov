import requests

url = "https://lindat.mff.cuni.cz/services/udpipe/api/process"


def udpipe_sent_lemmatize(sent: str) -> list[tuple[str, str]]:
    data = {
        "data": sent,
        "tokenizer": "",
        "tagger": "",
        "model": "old_church_slavonic-proiel-ud-2.15-241121",
    }

    response = requests.post(url, files=data)
    response.raise_for_status()

    result = []
    for l in response.json()["result"].split("\n"):
        if not l or l[0] == "#":
            continue
        p = l.split("\t")
        if not p[1].isalpha():
            continue
        result += [(p[1], p[2])]
    return result
