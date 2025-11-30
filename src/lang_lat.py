ms2color = {
    "V": "#90AA00",
}

ms2source = {
    "V": "syntacticus.gospel.vulgate",
}

udpipe_model = "latin-ittb-ud-2.15-241121"

# This is used for DB generation only. Runtime checks models available in memory
strans_models = [
    "sentence-transformers/LaBSE",  # 768
    "intfloat/multilingual-e5-base",  # 768
    # "nomic-ai/nomic-embed-text-v2-moe", #768
    "antoinelouis/colbert-xm",  # 768
    # "setu4993/LEALLA-small", #192
    # "setu4993/LEALLA-base", #192
    "bowphs/SPhilBerta",  # 768
]

examples = [
    "Lux in tenebris lucet",
    "Et lux in tenebris lucet, et tenebrae eam non comprehenderunt",
    "Agnus Dei, qui tollis peccata mundi, miserere nobis",
    "ditat Deus",
    "Ego sum via et veritas et vita",
    "Pater, dimitte illis, nesciunt enim quid faciunt",
    "Inimicus autem homo hoc fecit",
    "Nolite timere",
    "Beati pauperes spiritu, quoniam ipsorum est regnum caelorum",
]
