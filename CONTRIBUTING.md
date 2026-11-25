# Contributing

Corrections are welcome, especially anything that misstates the essay. For a misreading, please open an issue with the part or note number from [the original](https://commanding-heights.com/). For a fix you'd like to make yourself, open a pull request.

## Read it locally

It's a static site with no dependencies beyond Google Fonts.

```bash
open index.html
```

## Publish on GitHub Pages

1. Fork or push this folder to a repository.
2. Rebuild with your site's address, so the canonical link, social card and sitemap point to it:
   ```bash
   SITE_URL=https://YOUR-USERNAME.github.io/commanding-heights-guide/ ./build.sh
   ```
3. Commit, then go to **Settings → Pages → Deploy from a branch → `main` / root**.


## Narration

The Listen buttons play recorded MP3s from `audio/`, one per paragraph, generated with ElevenLabs. They stay hidden until the audio exists.

```bash
export ELEVENLABS_API_KEY=your-key        # never commit this
./build.sh --narration                    # refresh narration/script.json from the page
python3 narration/narrate.py --dry-run    # see how many characters it will use
python3 narration/narrate.py              # generate audio/ and audio/manifest.json
git add audio narration && git commit -m "Update narration" && git push
```

Only paragraphs whose text changed are regenerated. To change the voice, pass `--voice VOICE_ID` (the default is George, a warm British narrator).

## Editing

| File | Purpose |
|---|---|
| `page.html` | The source: styles, content and script in one file |
| `build.py` / `build.sh` | Builds `index.html` with search and social metadata, plus `robots.txt` and `sitemap.xml`. Run `./build.sh --card` to re-render the social card (needs Google Chrome). |
| `assets/social-card.*` | The 1200 × 630 preview image and its source |

Every section has an anchor (`#ravi`, `#brief`, `#value-chain`, `#parts`, `#pattern`, `#scissors`, `#line`, `#powers`, `#neo-dollar`, `#k-shape`, `#test`, `#firm`, `#allocator`, `#closing`, `#glossary`) for linking straight to it.
