#!/usr/bin/env bash
# Build the Pastel Bunny .ktheme package.
#
# A KakaoTalk iOS theme is just a ZIP of (KakaoTalk.css + Images/) with the
# extension renamed to .ktheme. This script (re)generates the images, then
# zips the contents of theme/ into dist/PastelBunny.ktheme.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

NAME="PastelBunny"
DIST="$ROOT/dist"
OUT="$DIST/$NAME.ktheme"

echo "==> Generating images"
python3 scripts/generate_images.py

echo "==> Packaging $NAME.ktheme"
mkdir -p "$DIST"
rm -f "$OUT"

# Zip from inside theme/ so KakaoTalk.css and Images/ sit at the archive root.
cd "$ROOT/theme"
zip -r -X "$OUT" KakaoTalk.css Images -x '.*' >/dev/null

echo "==> Done: dist/$NAME.ktheme"
unzip -l "$OUT" | sed 's/^/    /'
