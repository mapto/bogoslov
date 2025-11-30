#!/usr/bin/env bash

printf -v date '%(%Y%m%d)T' -1
echo "Date is $date"

echo "Creating 1-verses-$date.sql"
docker exec bogoslov-db-1 pg_dump -Ubogoslov -tverses bogoslov -a > 1-verses-$date.sql
gzip 1-verses-$date.sql

echo "Creating 2-ngrams-$date.sql"
docker exec bogoslov-db-1 pg_dump -Ubogoslov -tngrams bogoslov -a > 2-ngrams-$date.sql
gzip 2-ngrams-$date.sql

docker exec bogoslov-db-1 pg_dump -Ubogoslov -tembeddings bogoslov -a > 3-embeddings-$date.sql

# chu
declare -a models=("multilingual_en_uk_pl_ru" "LaBSE-en-ru-bviolet" "evenki-russian-parallel-corpora" "ru_oss" "bi-encoder-russian-msmarco" "sentence-transformers")
# lat
# declare -a models=("LaBSE" "multilingual-e5-base" "colbert-xm" "SPhilBerta")

for model in "${models[@]}"
do
   echo "Creating 3-embeddings-${model}-${date}.sql"
   head 3-embeddings-${date}.sql -n24 > 3-embeddings-${model}-${date}.sql
   cat 3-embeddings-${date}.sql | grep $model >> 3-embeddings-${model}-${date}.sql
   tail 3-embeddings-${date}.sql -n14 >> 3-embeddings-${model}-${date}.sql
   gzip 3-embeddings-${model}-${date}.sql
done

rm 3-embeddings-${date}.sql