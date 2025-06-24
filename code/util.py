from typing import Callable

import regex as re
from functools import reduce
import operator
from lxml import etree
from tqdm import tqdm

from tei_util import word_templ


def get_word_ranges(fulltext: str, ltext: str) -> list[tuple[str, int, int, str]]:
    """
    Returns list of lemmas, the corresponding indices in the original text, and the original word.


    >>> get_word_ranges("Hello, this is me", "hello this is me")
    [('hello', 0, 5, 'Hello'), ('this', 7, 11, 'this'), ('is', 12, 14, 'is'), ('me', 15, 17, 'me')]
    >>> get_word_ranges("Here goes nothing!", "here go nothing")
    [('here', 0, 4, 'Here'), ('go', 5, 9, 'goes'), ('nothing', 10, 17, 'nothing')]
    >>> get_word_ranges("стати и на", "стати и на")
    [('стати', 0, 5, 'стати'), ('и', 6, 7, 'и'), ('на', 8, 10, 'на')]

    >>> xml ='''<lg xmlns="http://www.tei-c.org/ns/1.0" id="1_2" n="2"><cl id="1_2_1">И въ законѣ его поѹчитъ сѧ дънъ и нощъ ⁘</cl><cl id="1_2_2">И бѫдетъ ꙗко дрѣво сажденое при исходищихъ водамъ  ⁘</cl></lg>'''
    >>> lemmas = 'и въ законъ и поучити себе дънъ и нощь и бꙑти ꙗко дрѣво садити при исходище вода'
    >>> get_word_ranges(xml, lemmas)
    [('и', 70, 71, 'И'), ('въ', 72, 74, 'въ'), ('законъ', 75, 81, 'законѣ'), ('и', 82, 85, 'его'), ('поучити', 86, 93, 'поѹчитъ'), ('себе', 94, 96, 'сѧ'), ('дънъ', 97, 101, 'дънъ'), ('и', 102, 103, 'и'), ('нощь', 104, 108, 'нощъ'), ('и', 130, 131, 'И'), ('бꙑти', 132, 138, 'бѫдетъ'), ('ꙗко', 139, 142, 'ꙗко'), ('дрѣво', 143, 148, 'дрѣво'), ('садити', 149, 157, 'сажденое'), ('при', 158, 161, 'при'), ('исходище', 162, 172, 'исходищихъ'), ('вода', 173, 179, 'водамъ')]
    """

    lltokens = [
        [e for e in re.split(r"\W+", s) if e]
        for s in re.split(r"<.+?>+", fulltext)
        if s
    ]
    # print(lltokens)
    ttokens = reduce(operator.concat, lltokens)
    ltokens = [e for e in re.split(r"\W+", ltext) if e]
    # TODO: when gaps in lemmatization, the match result is inaccurate
    # assert len(ttokens) == len(
    #     ltokens
    # ), f"Length of two texts is not equal:\n[{len(ttokens)}]: {ttokens[:100]}\n[{len(ltokens)}]: {ltokens[:100]}"
    result = []
    spos = 0
    epos = 0
    for i, lemma in enumerate(ltokens):
        spos = epos + fulltext[epos:].find(ttokens[i])
        epos = spos + fulltext[spos:].find(ttokens[i]) + len(ttokens[i])
        result += [(lemma, spos, epos, fulltext[spos:epos])]
    return result


def get_ngrams(fulltext: str, ltext: str, n: int = 3) -> dict[[tuple[str, ...], list]]:
    word_ranges = get_word_ranges(fulltext, ltext)
    ltokens = [e for e in re.split(r"\W+", ltext) if e]
    span = []
    result = {}
    for i, t in enumerate(ltokens):
        span += [t]
        if len(span) < n:
            continue
        ngram = tuple(span)
        if ngram not in result:
            result[ngram] = []
        spos = word_ranges[i - n + 1][1]
        epos = word_ranges[i][2]
        result[ngram] += [(spos, epos, fulltext[spos:epos])]
        # print(f"{i}/{spos} {i-n+1}/{epos}|{fulltext[spos:epos]}|{ttokens[i]}|{ttokens[i-n+1]}|{ngram}")
        span = span[1:]
    return result


def extract_text(node) -> str:
    return "".join(node.itertext()).strip()


def lemmatize_node(
    node, sentence_lemmatizer_func: Callable[[str], list[tuple[str, str]]]
) -> list[tuple[str, int, int]]:
    """
    Returns lemma, positions range, word and xml snippet in range
    >>> from lxml import etree
    >>> import re
    >>> node = etree.fromstring('''<lg id="1_1" n="1"><cl id="1_1_1">И на пѫти грьшънꙑхъ не ста .  </cl><cl id="1_1_2">И на сьдалищи гѹбителъ </cl><cl id="1_1_3">не сѣде .</cl><cl id="1_1_4">Нъ въ законѣ гдни волѣ его .</cl></lg>''')
    >>> lemmatize_node(node, lambda x: [(t, t) for t in re.split(r'\\W+', x) if t.strip()])
    [('И', 34, 35, 'И', 'И'), ('на', 36, 38, 'на', 'на'), ('пѫти', 39, 43, 'пѫти', 'пѫти'), ('грьшънꙑхъ', 44, 53, 'грьшънꙑхъ', 'грьшънꙑхъ'), ('не', 54, 56, 'не', 'не'), ('ста', 57, 60, 'ста', 'ста'), ('И', 84, 85, 'И', 'И'), ('на', 86, 88, 'на', 'на'), ('сьдалищи', 89, 97, 'сьдалищи', 'сьдалищи'), ('гѹбителъ', 98, 106, 'гѹбителъ', 'гѹбителъ'), ('не', 127, 129, 'не', 'не'), ('сѣде', 130, 134, 'сѣде', 'сѣде'), ('Нъ', 156, 158, 'Нъ', 'Нъ'), ('въ', 159, 161, 'въ', 'въ'), ('законѣ', 162, 168, 'законѣ', 'законѣ'), ('гдни', 169, 173, 'гдни', 'гдни'), ('волѣ', 174, 178, 'волѣ', 'волѣ'), ('его', 179, 182, 'его', 'его')]
    """
    xml = etree.tostring(node, encoding="unicode")
    text = extract_text(node)
    pairs = sentence_lemmatizer_func(text)
    ranges = [
        (l, s, e, w, xml[s:e])
        for (l, s, e, w) in get_word_ranges(
            xml, " ".join(p[1] for p in pairs if p[0].isalpha())
        )
    ]
    return ranges


def lemmatize_xml(
    fname: str, sentence_lemmatizer_func: Callable[[str], list[tuple[str, str]]]
) -> str:
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    ns_def = f''' xmlns="{ns['tei']}"'''
    root = etree.parse(fname, parser=etree.XMLParser())
    ranges = []
    xml = etree.tostring(root, encoding="unicode")
    for verse_id in tqdm(root.xpath("//tei:lg/@id", namespaces=ns)):
        # print(verse_id)
        node = root.xpath(f"//tei:lg[@id='{verse_id}']", namespaces=ns)[0]
        try:
            subxml = etree.tostring(node, encoding="unicode")
            subxml = subxml.replace(ns_def, "")
            # print(xml)
            # print(subxml)
            offset = xml.find(subxml) - len(ns_def)
            # print(offset)
            newranges = lemmatize_node(node, sentence_lemmatizer_func)
            newranges = [
                (
                    r[0],
                    r[1] + offset,
                    r[2] + offset,
                    r[3],
                    r[4],
                    xml[r[1] + offset : r[2] + offset],
                )
                for r in newranges
            ]
            ranges += newranges
            # print("verse", offset, newranges)
        except AssertionError:
            # print(verse_id)
            for line_id in root.xpath(
                f"//tei:lg[@id='{verse_id}']/tei:cl/@id", namespaces=ns
            ):
                # print(line_id)
                node2 = root.xpath(f"//tei:lg/tei:cl[@id='{line_id}']", namespaces=ns)[
                    0
                ]
                subxml = etree.tostring(node2, encoding="unicode")
                subxml = subxml.replace(ns_def, "")
                try:
                    offset = xml.find(subxml) - len(ns_def)
                    newranges = lemmatize_node(node2, sentence_lemmatizer_func)
                    newranges = [
                        (
                            r[0],
                            r[1] + offset,
                            r[2] + offset,
                            r[3],
                            r[4],
                            xml[r[1] + offset : r[2] + offset],
                        )
                        for r in newranges
                    ]
                    ranges += newranges
                    # print("line", offset, newranges)
                except AssertionError:
                    offset = xml.find(subxml)
                    spos = subxml.find(">") + 1
                    epos = subxml.rfind("<")
                    newranges = [
                        (
                            " ".join(
                                p[1]
                                for p in sentence_lemmatizer_func(subxml[spos:epos])
                            ),
                            spos + offset,
                            epos + offset,
                            xml[spos + offset : epos + offset],
                        )
                    ]
                    ranges += newranges
                    # print("multiword", offset, newranges)
    # return ranges
    for i, r in enumerate(reversed(ranges)):
        assert not any(
            char in r[0] for char in "<>"
        ), f"Lemma {r[0]} for word {xml[r[1]:r[2]]} contains non-compliant characters"
        ri = len(ranges) - i
        xml = (
            xml[: r[1]]
            + word_templ.format(
                pos=f"{verse_id}__{ri}", lemma=r[0], word=xml[r[1] : r[2]]
            )
            + xml[r[2] :]
        )
        # print(xml)
    return xml


if __name__ == "__main__":
    # src = "sample-tei.xml"
    # src = "sample-multiword-tei.xml"
    # src = "sample-verse-tei.xml"
    src = "sample-line-tei.xml"
    src = "sample-new-tei.xml"
    # src = "Bologna Psalter/BM1.tei.xml"
    func = lambda x: [(t, t) for t in re.split(r"\\W+", x) if t.strip()]
    result = lemmatize_xml(src, func)
    print(result)
