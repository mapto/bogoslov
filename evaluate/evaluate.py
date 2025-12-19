import requests
import pandas as pd

from settings import url_templ, loc_col, sim_col
from util import get_algorithms

methods = get_algorithms()


async def evaluate(query: str, locs: list[str], src="SBMZ", eval: str = ""):
    # print(query, expected)
    result = [
        ["query", "location", "row", "similarity", "original", "method", "src", "eval"]
    ]
    # words = len(query.split(" "))
    for m in methods:
        url = url_templ.format(method=m, src=src, query=query)
        with requests.get(url) as resp:
            resp.raise_for_status()
            if not resp.content:
                continue
            # print(r.content)
            data = resp.json()
            # print(data)
            rdf = pd.DataFrame(data)
        rdf["idx"] = rdf.index

        for loc in locs:
            match = rdf[rdf[loc_col].str.contains(loc)]
            for row in match.to_dict(orient="records"):
                # print(
                #     f"loc: {loc}; row: {r['idx']}; found: {r["found"]};similarity: {r[sim_col]}; method: {m}"
                # )
                res = [
                    query,
                    loc,
                    row["idx"],
                    row[sim_col],
                    row["found"],
                    m,
                    row["source"],
                    eval,
                ]
                result += [res]
                # print(row)
    return pd.DataFrame(result[1:], columns=result[0])
