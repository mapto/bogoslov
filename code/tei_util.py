tei_templ = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
<?xml-stylesheet type="text/xsl" href="file:///home/mapto/work/dllcm/BogoSlov/code/Bologna%20Psalter/ocs.xsl"?>
<teiHeader xml:lang="en">
  <sourceDesc>
    <bibl>{source}</bibl>
  </sourceDesc>
  <publicationStmt>
   <publisher>University of Milan</publisher>
   <pubPlace>Milano, Italy</pubPlace>
   <date>2025</date>
   <availability status="restricted">
    <licence target="https://creativecommons.org/licenses/by-nc-sa/4.0/"> Distributed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</licence>
   </availability>
  </publicationStmt>
</teiHeader>
<text xml:lang="cu">
 <body>
  <head>{title}</head>
  {body}
 </body>
</text>
</TEI>"""

chapter_templ = """ <div id="{number}" type="chapter" n="{number}">
{body} </div>
"""

verse_templ = """  <lg id="{chapter}_{name}" n="{name}">
{body}  </lg>
"""

line_templ = """   <cl id="{chapter}_{verse}_{line}">{text}</cl>
"""

word_templ = """<w lemma="{lemma}">{word}</w>"""
