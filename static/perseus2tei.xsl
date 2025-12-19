<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0">
  
  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
  
  <!-- Root template -->
  <xsl:template match="/">
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
      <xsl:apply-templates select="//tei:teiHeader"/>
      <xsl:apply-templates select="//tei:text"/>
    </TEI>
  </xsl:template>
  
  <!-- Transform teiHeader -->
  <xsl:template match="tei:teiHeader">
    <teiHeader xml:lang="en" xmlns="http://www.tei-c.org/ns/1.0">
      <publicationStmt>
        <publisher>Perseus Digital Library</publisher>
        <pubPlace>Tufts University, Medford MA, USA</pubPlace>
        <persName>Thibault Clérice</persName>
        <date>2014</date>
        <availability status="restricted">
          <licence target="http://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</licence>
        </availability>
      </publicationStmt>
      <sourceDesc>
          <bibl><link target="https://github.com/lascivaroma/latin-lemmatized-texts"/></bibl>
      </sourceDesc>
    </teiHeader>
  </xsl:template>
  
  <!-- Transform text element -->
  <xsl:template match="tei:text">
    <xsl:variable name="text-name" select="//tei:title/text()"/>
    <text xml:lang="lat" xmlns="http://www.tei-c.org/ns/1.0" >
      <body>
        <head>Jerome's Vulgate - <xsl:value-of select="$text-name"/></head>
        <xsl:apply-templates select="tei:body"/>
      </body>
    </text>
  </xsl:template>
  
  <!-- Transform body - group verses into chapters -->
  <xsl:template match="tei:body">
    <!-- Process chapter markers and verses -->
    <xsl:for-each select="tei:ab[@type='chapter']">
      <xsl:variable name="chapter-urn" select="@n"/>
      <xsl:variable name="chapter-num" select="substring-after(substring-after($chapter-urn, '-'), ':')"/>
      <xsl:variable name="text-name" select="//tei:title/text()"/>
      
      <div type="chapter" id="{$chapter-num}" n="{$text-name} {$chapter-num}" xmlns="http://www.tei-c.org/ns/1.0">
        <!-- Process all verses for this chapter -->
        <xsl:apply-templates select="following-sibling::tei:ab[@type='verse'][starts-with(@n, concat($chapter-urn, '.'))]" mode="verse-to-lg"/>
      </div>
    </xsl:for-each>
  </xsl:template>
  
  <!-- Transform verse (ab) to lg -->
  <xsl:template match="tei:ab[@type='verse']" mode="verse-to-lg">
    <xsl:variable name="verse-ref" select="@n"/>
    <xsl:variable name="verse-num" select="substring-after(substring-after($verse-ref, '-'), ':')"/>
    <xsl:variable name="chapter-verse" select="concat(substring-before($verse-num, '.'), '_', substring-after($verse-num, '.'))"/>
    
    <lg id="{$chapter-verse}" n="{substring-after($verse-num, '.')}" xmlns="http://www.tei-c.org/ns/1.0" >
      <xsl:apply-templates select="." mode="create-clauses"/>
    </lg>
  </xsl:template>
  
  <!-- Create clauses from verse content -->
  <xsl:template match="tei:ab[@type='verse']" mode="create-clauses">
    <xsl:variable name="verse-ref" select="@n"/>
    <xsl:variable name="verse-num" select="substring-after(substring-after($verse-ref, '-'), ':')"/>
    <xsl:variable name="chapter-verse" select="concat(substring-before($verse-num, '.'), '_', substring-after($verse-num, '.'))"/>
    <!-- <xsl:variable name="chapter-verse" select="concat(substring-after(substring-before(substring-after(substring-after($verse-ref, ':'), ':'), '.'), ':'), '_', substring-after(substring-after(substring-after($verse-ref, ':'), ':'), '.'))"/> -->
    
    <!-- For simplicity, create one clause per verse -->
    <cl id="{$chapter-verse}_1" xmlns="http://www.tei-c.org/ns/1.0" >
      <xsl:apply-templates select="tei:w" mode="word"/>
    </cl>
  </xsl:template>
  
  <!-- Transform word elements -->
  <xsl:template match="tei:w" mode="word">
    <w xmlns="http://www.tei-c.org/ns/1.0" >
      <xsl:attribute name="lemma">
        <xsl:apply-templates select="." mode="lemma"/>
      </xsl:attribute>
      <xsl:value-of select="."/>
    </w>
    <xsl:text> </xsl:text>
  </xsl:template>
  
 <xsl:template match="@lemma">
    <xsl:variable name="lastChar" select="substring(., string-length(.))"/>
    
    <xsl:attribute name="{name()}">
      <xsl:choose>
        <!-- Check if last character is a digit (0-9) -->
        <xsl:when test="translate($lastChar, '0123456789', '') = ''">
          <!-- Last char is a number, remove it -->
          <xsl:value-of select="substring(., 1, string-length(.) - 1)"/>
        </xsl:when>
        <xsl:otherwise>
          <!-- Last char is not a number, keep original value -->
          <xsl:value-of select="."/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

</xsl:stylesheet>
