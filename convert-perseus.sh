#!/usr/bin/env bash
src=../corpus/lascivaroma.bible.vulgate/
dest=../../bogoslov/corpora.lat/lascivaroma.bible.vulgate/

cd $src

for file in *; do 
    if [ -f "$file" ]; then 
      echo "$file"
      xsltproc ../../bogoslov/static/perseus2tei.xsl $file > "${dest}${file}"
      xsltproc ../../bogoslov/static/tei2html.xsl "${dest}${file}" > "${dest}${file/tei.xml/html}"
      echo "${dest}${file}"
      echo "${dest}${file/tei.xml/html}"
    fi 
done
