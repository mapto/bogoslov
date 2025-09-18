# BogoSlov

Biblical OriGins in slavOnic texts - Systems for Language-modelled Observation and Verification

A [SEED4EU+](https://4euplus.eu/4EU-1150.html) project. For further information, see (Ruskov et al 2025).

The contained corpora are courtesy to:

* Bologna Psalter: digitalisation by [Mary Catherine MacRobert](https://www.some.ox.ac.uk/our-people/catherine-mary-macrobert/), transliteration from Latin to Cyrillic by Martin Ruskov, TEI annotation by Martin Ruskov, Lemmatization with [UDPipe](https://lindat.mff.cuni.cz/services/udpipe/).

* Sinai Psalter, Codex Marianus, Codex Zographensis: [XSLT transformed](static/proiel2tei.xsl) from the [Syntacticus project](https://github.com/syntacticus/syntacticus-treebank-data). This source is aligned with the [Universal Dependencies](https://universaldependencies.org/) initiative and thus contains annotations, including human-validated lemmatization.

The BukyVede font is courtesy to [Kempgen and others](https://kodeks.de/AKSL/Schrift/BukyVedeBackground.htm).

# Installation

## Preparing the data

Make sure you have docker compose installed. We get started by creating the container image that will be used to deploy In the `code` directory run

    docker build -t bogoslov .

Then in the root directory initialize the data with

    docker compose up -f compose-init.yml

If you need to deploy to a machine where you cannot run the initialization scripts, make sure to export your data with:

    docker exec -it bogoslov-db-1 pg_dump -Ubogoslov -tverses bogoslov > ./db/init/dump-verses.sql
    docker exec -it bogoslov-db-1 pg_dump -Ubogoslov -tngrams bogoslov > ./db/init/dump-ngrams.sql
    docker exec -it bogoslov-db-1 pg_dump -Ubogoslov -tembeddings bogoslov > ./db/init/dump-embeddings.sql

Then make sure to have the exported files in the init directory of your deployment at the first launch of your `db` container.

## Running

After having initialized the data, run:

    docker compose up

Open http://localhost:8780 with your browser.

# Bibliography

Ruskov, Mikulka, Podtergera, Gavrilkov & Thompson (2025). Quotes at the Fingertips: The BogoSlov Project’s Combined Approach towards Identification of Biblical Material in Old Church Slavonic Texts. In Proceedings of the 21st Conference on Information and Research Science Connecting to Digital and Library Science. CEUR-WS. https://ceur-ws.org/Vol-3937/short8.pdf ([bibtex](static/references.bib))
