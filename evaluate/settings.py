# sfile = "Gospel Quotations and Allusions.xlsx"
# test_col = "Quotation"
# res_col = "Attribution"
# src = "MZ"

# sfile = "Clozianus quotations.xlsx"
# test_col = "full quotation"
# res_col = "verse"
# src = "MZ"

# sfile = "Psalms quotations.xlsx"
# test_col = "text"
# res_col = "attribution/place"
# src = "SB"

# efile = "../results/lcs-BMSZ-ac3cb180f466a148f5a17264d531c0ba.xlsx"
# efile = "strans-BMSZ-602150b37d8b445058898b7306c90427.xlsx"
query_col = "query"
# sim_col = "similarity"
sim_col = "accuracy"
loc_col = "location"
method_col = "method"

url_root = "http://localhost:8780"

url_templ = url_root + "/api/{method}?sources={src}&fulltext={query}&result_format=json"

url_settings = url_root + "/settings"
