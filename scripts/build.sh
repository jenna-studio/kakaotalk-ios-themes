#!/usr/bin/env bash
# Build a KakaoTalk .ktheme package for one of the themes in themes/.
#
# A KakaoTalk iOS theme is just a ZIP of (KakaoTalkTheme.css + Images/) with the
# extension renamed to .ktheme. This script (re)generates that theme's images,
# then zips the contents of themes/<name>/ into dist/<ThemeName>.ktheme.
#
# Usage:
#   ./scripts/build.sh                 # builds every theme under themes/
#   ./scripts/build.sh kittytalk       # builds just themes/kittytalk
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DIST="$ROOT/dist"
mkdir -p "$DIST"

build_one() {
  local dir="$1"
  local name
  name="$(basename "$dir")"
  local css="$dir/KakaoTalkTheme.css"

  [ -f "$css" ] || { echo "!! skip $name (no KakaoTalkTheme.css)"; return; }

  echo "==> [$name] generating images"
  if [ -f "$dir/scripts/generate_images.py" ]; then
    python3 "$dir/scripts/generate_images.py"
  fi

  # Package name = ManifestStyle theme-name with spaces removed, else dir name.
  local pkg
  pkg="$(sed -n "s/.*-kakaotalk-theme-name:[^']*'\([^']*\)'.*/\1/p" "$css" | head -1 | tr -d ' ')"
  pkg="${pkg:-$name}"
  local out="$DIST/$pkg.ktheme"

  echo "==> [$name] packaging $pkg.ktheme"
  rm -f "$out"
  # Zip from inside the theme dir so KakaoTalkTheme.css and Images/ sit at the
  # archive root. -D omits directory entries (some importers reject "Images/").
  ( cd "$dir" && zip -r -D -X "$out" KakaoTalkTheme.css Images -x '.*' >/dev/null )

  echo "==> [$name] done: dist/$pkg.ktheme"
  unzip -l "$out" | sed 's/^/    /'
}

if [ "$#" -ge 1 ]; then
  build_one "$ROOT/themes/$1"
else
  for d in "$ROOT"/themes/*/; do
    build_one "${d%/}"
  done
fi
