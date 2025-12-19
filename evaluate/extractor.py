import pandas as pd

from util import _parse_res_col


class Extractor:
    @staticmethod
    def build(surl: str) -> "Extractor":
        if "1YRBLiZqsTPZEBiyuZ01-gKxcPyl9VT0IoNE_07X0Hsg" in surl:
            print("Psalms")
            test_col = "text"
            res_col = "attribution/place"
            src = "SB"
            addr_sep = ","
            list_sep = "."
        elif "1xppiRNK4cCHHW3GqDCL8tliAeZDPg87PTfME80rnvE4" in surl:
            print("Gospels")
            test_col = "Quotation"
            res_col = "Attribution"
            src = "MZ"
            addr_sep = ":"
            list_sep = ","
        elif "1hBilgcFMrdbnLkqM2x21ke42WZaAbyFJ" in surl:
            print("Clozianus")
            test_col = "full quotation"
            res_col = "verse"
            addr_sep = ","
            list_sep = "/"
            if "1370115719" in surl:
                print("Psalms")
                src = "SB"
            elif "945687746" in surl:
                print("Gospels")
                src = "MZ"
            else:
                raise NotImplementedError("Unexpected sheet")
        else:
            raise NotImplementedError("Unexpected source")

        return Extractor(surl, test_col, res_col, src, addr_sep, list_sep)

    def __init__(
        self,
        surl: str,
        test_col: str,
        res_col: str,
        src: str,
        addr_sep=":",
        list_sep=",",
    ):
        sfile = surl.replace("/edit?gid=", "/export?format=xlsx&gid=")
        self.df = pd.read_excel(sfile, engine="openpyxl")
        self.test_col = test_col
        self.res_col = res_col
        self.src = src
        self.addr_sep = addr_sep
        self.list_sep = list_sep
        self.sname = surl.replace(
            "https://docs.google.com/spreadsheets/d/", ""
        ).replace("/edit?gid=", "-")
        self.fname = "evaluation-" + self.sname + ".xlsx"
        print(self.sname)

    def __iter__(self):
        for _, r in self.df.iterrows():
            test = r[self.test_col]
            if not test or pd.isna(test):
                continue
            res = r[self.res_col]
            if not res or pd.isna(res):
                continue
            yield (
                test,
                _parse_res_col(str(res), self.addr_sep, self.list_sep),
                self.src,
            )

    async def __aiter__(self):
        for _, r in self.df.iterrows():
            test = r[self.test_col]
            if not test or pd.isna(test):
                continue
            res = r[self.res_col]
            if not res or pd.isna(res):
                continue
            yield (
                test,
                _parse_res_col(str(res), self.addr_sep, self.list_sep),
                self.src,
            )

    def __len__(self) -> int:
        return (
            self.df[self.test_col].notna()
            & self.df[self.test_col].astype(bool)
            & self.df[self.res_col].notna()
            & self.df[self.res_col].astype(bool)
        ).sum()
