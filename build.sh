#!/bin/sh
# Builds index.html, robots.txt and sitemap.xml from page.html, and renders the social card.
# --narration re-exports narration/script.json from the page; --card re-renders the social card.
# Usage: SITE_URL=https://you.github.io/commanding-heights-guide/ ./build.sh
set -e
cd "$(dirname "$0")"
python3 build.py
if [ "$1" = "--narration" ]; then
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --virtual-time-budget=5000 \
    --dump-dom "file://$(pwd)/index.html?export-narration" 2>/dev/null | python3 -c '
import re,sys,json
m=re.search(r"<script type=\"application/json\" id=\"narration-export\">(.*?)</script>",sys.stdin.read(),re.S)
items=json.loads(m.group(1));open("narration/script.json","w").write(json.dumps(items,ensure_ascii=False,indent=1))
print("Exported",len(items),"paragraphs to narration/script.json")'
fi
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ "$1" = "--card" ] && [ -x "$CHROME" ]; then
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,630 \
    --virtual-time-budget=4000 --screenshot="$(pwd)/assets/social-card.png" "file://$(pwd)/assets/social-card.html" >/dev/null 2>&1
  echo "Rendered assets/social-card.png"
fi
