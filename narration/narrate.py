#!/usr/bin/env python3
"""Generate the companion's audio narration with ElevenLabs.

Reads narration/script.json (one entry per paragraph, exported from the page),
writes one MP3 per paragraph into audio/, and writes audio/manifest.json, which
the page's Listen player reads. Paragraphs that already have audio are skipped,
so after editing the page you only pay for what changed.

Usage (from the repo root):
  export ELEVENLABS_API_KEY=...        # your key; never commit it
  python3 narration/narrate.py --dry-run      # count characters, spend nothing
  python3 narration/narrate.py                # generate
  python3 narration/narrate.py --voice VOICE_ID --model eleven_multilingual_v2

Refresh script.json after editing the page:  ./build.sh --narration
"""
import argparse, hashlib, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "narration" / "script.json"
AUDIO = ROOT / "audio"
INTRO = ("This is an independent companion to The Commanding Heights, prepared by Rhet Porter. "
         "It is not written or endorsed by the essay's authors, Will Manidis and Joe Roberts. The narration uses an AI voice.")

# How names should sound. The page keeps the real spelling; only the audio uses these.
PRONOUNCE = {
    "Manidis": "Man-eye-dis",
    "Rhet Porter": "Rhett Porter",
}

def spoken(text):
    for word, say in PRONOUNCE.items():
        text = text.replace(word, say)
    return text

def clip_name(text, voice):
    # keyed on what is spoken, so a pronunciation fix regenerates only the clips it touches
    return hashlib.sha1((voice + "|" + spoken(text)).encode("utf-8")).hexdigest()[:14] + ".mp3"

def duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, check=True).stdout.strip()
        return round(float(out), 2)
    except Exception:
        return round(path.stat().st_size / 16000, 2)  # rough fallback for 128 kbps

def tts(key, voice, model, text, prev, nxt):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
    body = {"text": text, "model_id": model, "previous_text": prev[-600:], "next_text": nxt[:600],
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": True}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(2 ** attempt * 2); continue
            sys.exit(f"ElevenLabs error {e.code}: {msg}")
        except urllib.error.URLError as e:
            if attempt < 4: time.sleep(2 ** attempt * 2); continue
            sys.exit(f"Network error: {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default=os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"),
                    help="ElevenLabs voice ID (default: George, a warm British narrator)")
    ap.add_argument("--model", default="eleven_multilingual_v2")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    items = json.loads(SCRIPT.read_text(encoding="utf-8"))
    AUDIO.mkdir(exist_ok=True)
    todo = [(i, it) for i, it in enumerate(items) if not (AUDIO / clip_name(it["text"], a.voice)).exists()]
    intro_file = AUDIO / clip_name(INTRO, a.voice)
    chars = sum(len(it["text"]) for _, it in todo) + (0 if intro_file.exists() else len(INTRO))
    print(f"{len(items)} paragraphs, {len(todo)} need audio, {chars:,} characters to generate.")
    if a.dry_run:
        return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY first (export ELEVENLABS_API_KEY=...).")

    if not intro_file.exists():
        intro_file.write_bytes(tts(key, a.voice, a.model, spoken(INTRO), "", spoken(items[0]["text"])))
    for n, (i, it) in enumerate(todo, 1):
        prev = items[i - 1]["text"] if i else ""
        nxt = items[i + 1]["text"] if i + 1 < len(items) else ""
        (AUDIO / clip_name(it["text"], a.voice)).write_bytes(tts(key, a.voice, a.model, spoken(it["text"]), spoken(prev), spoken(nxt)))
        print(f"  {n}/{len(todo)}  {it['section']}: {it['text'][:60]}")

    clips = []
    for it in items:
        f = AUDIO / clip_name(it["text"], a.voice)
        clips.append({"section": it["section"], "text": it["text"], "file": f.name, "seconds": duration(f)})
    manifest = {"voice": a.voice, "model": a.model, "credit": "AI narration · ElevenLabs",
                "intro": {"file": intro_file.name, "seconds": duration(intro_file)}, "clips": clips}
    (AUDIO / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    keep = {c["file"] for c in clips} | {intro_file.name, "manifest.json"}
    for f in AUDIO.glob("*.mp3"):
        if f.name not in keep:
            f.unlink()
    total = sum(c["seconds"] for c in clips) / 60
    print(f"Done: {len(clips)} clips, {total:.1f} minutes. Commit audio/ and push.")

if __name__ == "__main__":
    main()
