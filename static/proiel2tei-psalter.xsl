<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<?xml-stylesheet type="text/xsl" href="/tei2html.xsl"?>
  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
  
  <!-- Root template -->
  <xsl:template match="/proiel">
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader xml:lang="en">
        <sourceDesc>
          <bibl>Hanne Martine Eckhoff and Aleksandrs Berdicevskis, https://munin.uit.no/handle/10037/22366</bibl>
        </sourceDesc>
        <publicationStmt>
          <publisher>Institute for Literature, Bulgarian Academy of Sciences</publisher>
          <pubPlace>Sofia, Bulgaria</pubPlace>
          <date>2015</date>
          <availability status="restricted">
            <licence target="{source/license-url}">
              <xsl:value-of select="source/license"/>
            </licence>
          </availability>
        </publicationStmt>
      </teiHeader>
      <text xml:lang="chu">
        <body>
          <head>
            <xsl:value-of select="source/title"/>
          </head>
          <xsl:apply-templates select="source/div"/>
        </body>
      </text>
    </TEI>
  </xsl:template>
  
  <!-- Template for div elements -->
  <xsl:template match="div">
    <div xmlns="http://www.tei-c.org/ns/1.0" id="{substring-after(title, ' ')}" type="chapter" n="{title}">
      <xsl:apply-templates select="sentence"/>
    </div>
  </xsl:template>
  
  <!-- Template for sentence elements -->
  <xsl:template match="sentence">
    <lg xmlns="http://www.tei-c.org/ns/1.0" id="{substring-after(parent::div/title, ' ')}_{position()}" n="{position()}">
      <cl xmlns="http://www.tei-c.org/ns/1.0" id="{substring-after(parent::div/title, ' ')}_{position()}_1">
        <xsl:apply-templates select="token[@form]"/>
      </cl>
    </lg>
  </xsl:template>
  
  <!-- Template for token elements -->
  <xsl:template match="token[@form]">
    <w xmlns="http://www.tei-c.org/ns/1.0" lemma="{@lemma}">
      <xsl:value-of select="@form"/>
    </w>
    <xsl:if test="@presentation-after">
      <xsl:value-of select="@presentation-after"/>
    </xsl:if>
  </xsl:template>
  
  <!-- Template for token elements -->
  <xsl:template match="token[@citation-part]">
    <cl xmlns="http://www.tei-c.org/ns/1.0" id="{@lemma}">
      <xsl:value-of select="@citation-part"/>
    </cl>
    <xsl:if test="@presentation-after">
      <xsl:value-of select="@presentation-after"/>
    </xsl:if>
  </xsl:template>
  

  <!-- Template to ignore empty tokens -->
  <xsl:template match="token[not(@form)]"/>
  
</xsl:stylesheet>