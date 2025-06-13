<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                exclude-result-prefixes="tei">
    
    <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-public="-//W3C//DTD HTML 4.01//EN"/>
    
    <!-- Root template -->
    <xsl:template match="/">
        <html>
            <head>
                <title>TEI Document</title>
                <meta charset="UTF-8"/>
                <link rel="stylesheet" href="../ocs.css"/>
            </head>
            <body>
                <xsl:apply-templates select="//tei:body"/>
            </body>
        </html>
    </xsl:template>
    
    <!-- Template for body -->
    <xsl:template match="tei:body">
        <xsl:apply-templates/>
    </xsl:template>
    
    <!-- Template for head -->
    <xsl:template match="tei:head">
        <h1>
            <xsl:if test="@id">
                <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </h1>
    </xsl:template>
    
    <!-- Template for div (chapters) -->
    <xsl:template match="tei:div">
        <div class="chapter">
            <xsl:if test="@id">
                <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
            </xsl:if>
            <xsl:if test="@n">
                <h2><xsl:value-of select="@n"/></h2>
            </xsl:if>
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    
    <!-- Template for lg (line groups) -->
    <xsl:template match="tei:lg">
        <div class="lg">
            <xsl:if test="@id">
                <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </div>
    </xsl:template>
    
    <!-- Template for cl (clauses/lines) -->
    <xsl:template match="tei:cl">
        <span class="cl">
            <xsl:if test="@id">
                <xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </span>
        <xsl:if test="position() != last()">
            <br/>
        </xsl:if>
    </xsl:template>
    
    <!-- Template for text content -->
    <xsl:template match="text()">
        <xsl:value-of select="."/>
    </xsl:template>
    
</xsl:stylesheet>