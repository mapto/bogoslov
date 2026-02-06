#!/usr/bin/env bash

xsltproc static/proiel2tei-gospel.xsl ../corpus/proiel/marianus.proiel.xml > ../corpus/proiel/marianus.tei.xml
xsltproc static/proiel2tei-gospel.xsl ../corpus/proiel/zogr.proiel.xml > ../corpus/proiel/zogr.tei.xml
xsltproc static/proiel2tei-psalter.xsl ../corpus/proiel/psal-sin.proiel.xml > ../corpus/proiel/psal-sin.tei.xml