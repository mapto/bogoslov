import requests
import regex as re

from settings import url_settings

gospel_map = {
    "Matt": "matthaeo",
    "Lk": "luca",
    "Jo": "ioanne",
    "Mk": "marco",
    "Matth.": "matthaeo",
    "Luc.": "luca",
    "Jo.": "ioanne",
    "Ps": "ps",
    "Ps.": "ps",
}


def _parse_res_col(text: str, addr_sep: str = ":", list_sep=",") -> list[str]:
    """
    >>> _parse_res_col("Matt 19:6")
    ['matthaeo 19.6']

    >>> _parse_res_col("Matt 25:18")
    ['matthaeo 25.18']

    >>> _parse_res_col("Lk 6:27-29; Matt 5:44,39")
    ['luca 6.27', 'luca 6.28', 'luca 6.29', 'matthaeo 5.44', 'matthaeo 5.39']

    >>> _parse_res_col("Ps 73,12", addr_sep=",")
    ['ps 73.12']

    >>> _parse_res_col("Ps 8, 3", addr_sep=",")
    ['ps 8.3']

    >>> _parse_res_col("  Ps. 136, 1-2; Ps. 137, 1-2", addr_sep=",")
    ['ps 136.1', 'ps 136.2', 'ps 137.1', 'ps 137.2']

    >>> _parse_res_col(" Matth. 27,  4", addr_sep=",")
    ['matthaeo 27.4']

    >>> _parse_res_col("Ps 75,9/10", addr_sep=",", list_sep="/")
    ['ps 75.9', 'ps 75.10']
    """
    text = text.split("~")[0].strip()
    text = re.sub(addr_sep + r"\s+", addr_sep, text)
    quots = [p.strip() for p in text.split(";")]
    result = []
    for q in quots:
        parts = [p.strip() for p in q.strip().replace(addr_sep, ".").split(" ")]
        assert len(parts) == 2, f"Unexpected row: {q}"
        book = gospel_map[parts[0]]

        if list_sep in parts[1]:
            pparts = parts[1].split(list_sep)
            lloc = pparts[0].split(".")[0].strip()
            result += [f"{book} {pparts[0]}"]
            for loc in pparts[1:]:
                if "." in loc:
                    result += [f"{book} {loc}"]
                else:
                    result += [f"{book} {lloc}.{loc}"]

        elif "-" in parts[1]:
            pp = [p.strip() for p in parts[1].split(".")]
            lloc = pp[0]
            ppp = [p.strip() for p in pp[1].split("-")]
            for loc2 in range(int(ppp[0]), int(ppp[1]) + 1):
                result += [f"{book} {lloc}.{loc2}"]

        else:
            result += [f"{book} {parts[1]}"]

    return result


def get_algorithms() -> list[str]:
    response = requests.get(url_settings)
    response.raise_for_status()
    data = response.json()
    return data["explicit_algorithms"] + list(
        data["sentence_transformer_models"].keys()
    )
