#!/bin/sh
# Generate the narration, then commit and push it.
# Asks for your ElevenLabs key without showing it; the key is never saved or committed.
set -e
cd "$(dirname "$0")/.."
python3 narration/narrate.py --dry-run
while [ -z "$ELEVENLABS_API_KEY" ]; do
  printf "Paste your ElevenLabs API key (it stays hidden), then press Enter: "
  stty -echo; IFS= read -r ELEVENLABS_API_KEY; stty echo; echo
  ELEVENLABS_API_KEY=$(printf %s "$ELEVENLABS_API_KEY" | tr -d '[:space:]')
  K=$ELEVENLABS_API_KEY; N=${#K}
  if [ $((N % 2)) -eq 0 ] && [ "$N" -gt 60 ]; then H=$((N / 2)); A=$(printf %s "$K" | cut -c1-$H); B=$(printf %s "$K" | cut -c$((H + 1))-); [ "$A" = "$B" ] && ELEVENLABS_API_KEY=$A && echo "It looks like the key was pasted twice. Using it once."; fi
  case "$ELEVENLABS_API_KEY" in
    "") echo "Nothing was pasted. Try again: Cmd-V once, then Enter." ;;
    sk_*) if [ ${#ELEVENLABS_API_KEY} -gt 60 ]; then echo "That's ${#ELEVENLABS_API_KEY} characters, longer than one key. Paste it just once."; ELEVENLABS_API_KEY=""; else echo "Got a key (${#ELEVENLABS_API_KEY} characters, starts with sk_)."; fi ;;
    *) echo "That doesn't start with sk_, so it may not be the API key. Copy the key again and paste it once."; ELEVENLABS_API_KEY="" ;;
  esac
done
export ELEVENLABS_API_KEY
python3 narration/narrate.py
git add audio narration
git commit -q -m "Update narration"
git push -q
echo "Pushed. The Listen buttons appear on the live site in about a minute."
