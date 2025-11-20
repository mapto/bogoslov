import requests
from settings import udpipe_model

url = "https://lindat.mff.cuni.cz/services/udpipe/api/process"


def udpipe_sent_lemmatize(sent: str) -> list[tuple[str, str]]:
    """
    >>> udpipe_sent_lemmatize("речено б҃ъіⷭ҇ азъ г҃л҄ѭ вамъ· не противити сѧ зълоу ѣко речено бъіⷭ҇  ѣко ꙇ оц҃ь вашь нб҃с(къ) съвръшенъ естъ· ко҃н· за҃ч")
    [('речено', 'рещи'), ('б҃ъіⷭ҇', 'бꙑти'), ('азъ', 'азъ'), ('г҃л҄ѭ', 'глаголати'), ('вамъ·', 'ваꙑ'), ('не', 'не'), ('противити', 'противити'), ('сѧ', 'себе'), ('зълоу', 'зълъ'), ('ѣко', 'ꙗко'), ('речено', 'рещи'), ('бъіⷭ҇', 'бꙑти'), ('ѣко', 'ꙗко'), ('ꙇ', 'и'), ('оц҃ь', 'отьць'), ('вашь', 'вашь'), ('нб҃с(къ)', 'небесьскъ'), ('съвръшенъ', 'съврьшенъ'), ('естъ·', 'бꙑтъи'), ('ко҃н·', 'нъ'), ('за҃ч', 'задити')]

    >>> udpipe_sent_lemmatize("аще ты хощеши, можеть сїе тебѣ богъ дати")
    [('аще', 'аще'), ('ты', 'тꙑ'), ('хощеши,', 'хощтѣти'), ('можеть', 'мощи'), ('сїе', 'сь'), ('тебѣ', 'тꙑ'), ('богъ', 'богъ'), ('дати', 'дати')]
    """
    data = {
        "data": sent,
        "tokenizer": "",
        "tagger": "",
        "model": udpipe_model,
    }

    response = requests.post(url, files=data)
    response.raise_for_status()

    result = []
    for lem in response.json()["result"].split("\n"):
        if not lem or lem[0] == "#":
            continue
        p = lem.split("\t")
        result += [(p[1], p[2])]
    return result


if __name__ == "__main__":
    pass
