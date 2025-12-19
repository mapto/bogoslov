ms2color = {
    "O": "#90AA00",
}

ms2source = {
    "O": "syntacticus.gospel.octava",
}

udpipe_model = "greek-gdt-ud-2.17-251125"

# This is used for DB generation only. Runtime checks models available in memory
strans_models = [
    "sentence-transformers/LaBSE",  # 768
    "intfloat/multilingual-e5-base",  # 768
    # "nomic-ai/nomic-embed-text-v2-moe", #768
    # "antoinelouis/colbert-xm",  # 768
    # "setu4993/LEALLA-small", #192
    # "setu4993/LEALLA-base", #192
    "bowphs/SPhilBerta",  # 768
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",  # 768
]

examples = [
    "Ἰατρέ, θεράπευσον σεαυτόν",
    "Ἰησοῦς Χριστὸς Θεοῦ Υἱὸς Σωτήρ",
    "ναὶ ναί, οὒ οὔ",
    "Σὺν Ἀθηνᾷ καὶ χεῖρα κίνει",
    "Ego sum via et veritas et vita",
    "βασιλεία τῶν οὐρανῶν",
    "υἱὸς μονογενής",
]
