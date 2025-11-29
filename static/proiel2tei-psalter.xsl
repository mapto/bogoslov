<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
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
      <text>
        <xsl:attribute name="xml:lang">
          <xsl:value-of select="source/@language"/>
        </xsl:attribute>
        <body>
          <head>
            <xsl:value-of select="source/title"/>
          </head>
          <xsl:apply-templates select="source/div"/>
        </body>
      </text>
    </TEI>
  </xsl:template>

  <!-- Template for div elements (psalms) -->
    <xsl:template match="div">
        <xsl:variable name="chapter-num">
            <xsl:value-of select="substring-after(title, ' ')"/>
        </xsl:variable>
        
        <div xmlns="http://www.tei-c.org/ns/1.0" type="chapter">
            <xsl:attribute name="id">
                <xsl:value-of select="$chapter-num"/>
            </xsl:attribute>
            <xsl:attribute name="n">
                <xsl:value-of select="concat('Ps ', $chapter-num)"/>
            </xsl:attribute>
            
            <xsl:apply-templates select="sentence"/>
        </div>
    </xsl:template>

    <!-- Template for sentence elements -->
    <xsl:template match="sentence">
        <!-- Extract verse number from citation-part of first token -->
        <xsl:variable name="address" select="token[@citation-part][1]/@citation-part"/>
        <xsl:variable name="verse-num">
            <xsl:value-of select="substring-after($address, '.')"/>
        </xsl:variable>
        <xsl:variable name="book-chapter">
            <xsl:value-of select="substring-before($address, '.')"/>
        </xsl:variable>
        
        <!-- Group sentences by verse -->
        <xsl:if test="not(preceding-sibling::sentence[substring-before(substring-after(token[@citation-part][1]/@citation-part, ' '), '.') = $book-chapter and substring-after(substring-after(token[@citation-part][1]/@citation-part, ' '), '.') = $verse-num])">
            <lg xmlns="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="id">
                   <xsl:value-of select="concat($book-chapter, '_', $verse-num)"/>
                </xsl:attribute>
                <xsl:attribute name="n">
                    <xsl:value-of select="$verse-num"/>
                </xsl:attribute>
                
                <!-- Process all sentences with the same verse number -->
                <xsl:apply-templates select=". | following-sibling::sentence[substring-before(token[@citation-part][1]/@citation-part, '.') = $book-chapter and substring-after(token[@citation-part][1]/@citation-part, '.') = $verse-num]" mode="clause"/>
            </lg>
        </xsl:if>
    </xsl:template>
    
    <!-- Template for processing sentences as clauses -->
    <xsl:template match="sentence" mode="clause">
        <xsl:variable name="citation" select="token[@citation-part][1]/@citation-part"/>
        <xsl:variable name="address" select="$citation"/>
        <xsl:variable name="verse-num">
            <xsl:value-of select="substring-after($address, '.')"/>
        </xsl:variable>
        <xsl:variable name="book-chapter">
            <xsl:value-of select="substring-before($address, '.')"/>
        </xsl:variable>
        <xsl:variable name="sentence-num">
            <xsl:number count="sentence[substring-before(token[@citation-part][1]/@citation-part, '.') = $book-chapter and substring-after(token[@citation-part][1]/@citation-part, '.') = $verse-num]"/>
        </xsl:variable>
        
        <l xmlns="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="id">
                <xsl:variable name="verse-id">
                    <xsl:value-of select="concat($book-chapter, '_', $verse-num)"/>
                </xsl:variable>
                <xsl:value-of select="concat($verse-id, '_', $sentence-num)"/>
            </xsl:attribute>
            
            <!-- Process tokens, excluding empty tokens -->
            <xsl:for-each select="token[@form]">
                <w xmlns="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="lemma">
                        <xsl:value-of select="@lemma"/>
                    </xsl:attribute>
                    <xsl:value-of select="@form"/>
                </w>
                <xsl:if test="@presentation-after and @presentation-after != ' '">
                    <xsl:value-of select="@presentation-after"/>
                </xsl:if>
                <xsl:if test="position() != last() and not(@presentation-after) or @presentation-after = ' '">
                    <xsl:text> </xsl:text>
                </xsl:if>
            </xsl:for-each>
        </l>
    </xsl:template>
  
</xsl:stylesheet>
