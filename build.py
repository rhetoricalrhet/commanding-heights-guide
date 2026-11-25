#!/usr/bin/env python3
"""Build index.html (a full, search-friendly document) from page.html.

page.html is the source: head tags, styles, content and script in one file.
Set SITE_URL to the address the site is served from, e.g.
  SITE_URL=https://example.github.io/commanding-heights-guide/ ./build.sh
"""
import json, os, re, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SITE = os.environ.get("SITE_URL", "https://rhetoricalrhet.github.io/commanding-heights-guide/").rstrip("/") + "/"
TITLE = "The Commanding Heights: A Reader’s Companion (Unofficial)"
DESC = ("An unofficial, independent reader’s companion by Rhet Porter to “The Commanding Heights” by Will Manidis and Joe Roberts: "
        "the argument, fourteen data figures, a part-by-part guide, a glossary and an audio read-aloud. Not written or endorsed by the authors.")
TODAY = datetime.date.today().isoformat()

src = (ROOT / "page.html").read_text(encoding="utf-8")
cut = src.index("<style>")
head_tags, rest = src[:cut], src[cut:]
style_end = rest.index("</style>") + len("</style>")
style, body = rest[:style_end], rest[style_end:]
# the page's own <title> and description are replaced by the SEO versions below
head_tags = re.sub(r"<title>.*?</title>\s*", "", head_tags, flags=re.S)
head_tags = re.sub(r'<meta name="description"[^>]*>\s*', "", head_tags)

ld = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "The Commanding Heights: A Reader’s Companion",
  "alternativeHeadline": "An unofficial illustrated guide to the essay by Will Manidis and Joe Roberts",
  "description": DESC,
  "url": SITE,
  "image": SITE + "assets/social-card.png",
  "inLanguage": "en",
  "dateModified": TODAY,
  "isAccessibleForFree": True,
  "author": {"@type": "Person", "name": "Rhet Porter", "url": "https://github.com/rhetoricalrhet"},
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "isBasedOn": {
    "@type": "Article",
    "name": "The Commanding Heights",
    "url": "https://commanding-heights.com/",
    "datePublished": "2026-10-29",
    "author": [{"@type": "Person", "name": "Will Manidis"}, {"@type": "Person", "name": "Joe Roberts"}]
  },
  "about": ["artificial intelligence economics", "AI infrastructure investment", "stablecoins and the US dollar", "AI and labor", "private equity"],
}

favicon = ("data:image/svg+xml," +
  "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23fff'/%3E"
  "%3Cpath d='M16 6 L27 25 H5 Z' fill='%232b6a55'/%3E%3C/svg%3E")

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Rhet Porter (companion; not the essay’s authors)">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{favicon}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="The Commanding Heights: A Reader’s Companion">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}assets/social-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Commanding Heights, a reader's companion. Unofficial, not by the authors.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}assets/social-card.png">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head_tags.strip()}
{style}
</head>
<body>
"""
(ROOT / "index.html").write_text(head + body.strip() + "\n</body>\n</html>\n", encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
(ROOT / "sitemap.xml").write_text(
  f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
  f"  <url><loc>{SITE}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq></url>\n</urlset>\n", encoding="utf-8")
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("Built index.html, robots.txt, sitemap.xml for", SITE)
