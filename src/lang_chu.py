ms2color = {
    "S": "#90AA00",
    "B": "#00AA90",
    "M": "#0090AA",
    "Z": "#9000AA",
}

ms2source = {
    "S": "psalter.sinai.syntacticus",
    "B": "psalter.bologna.oxford",
    "M": "gospel.marianus.syntacticus",
    "Z": "gospel.zographensis.syntacticus",
}

udpipe_model = "old_church_slavonic-proiel-ud-2.15-241121"

strans_models = [
    "uaritm/multilingual_en_uk_pl_ru",  # 768
    # "cointegrated/rubert-tiny2", # 312
    "pouxie/LaBSE-en-ru-bviolet",  # 768
    # "Den4ikAI/sbert_large_mt_ru_retriever",  # 1024
    # "siberian-lang-lab/evenki-russian-parallel-corpora",  # 768
    # "Diiiann/ru_oss",  # 768
    # "DiTy/bi-encoder-russian-msmarco",  # 768
    # "BounharAbdelaziz/ModernBERT-Arabic-Embeddings", # 768, restricted access
    "sentence-transformers/LaBSE",  # 768
]

examples = [
    "богомъ",
    "въса землꙗ да поклонит ти се и поеть тебе",
    "Приде же въ градъ самарьскъ",
    "Не осѫждаите да не осѫждени бѫдете",
]
