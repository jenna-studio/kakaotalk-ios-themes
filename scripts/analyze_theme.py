#!/usr/bin/env python3
"""
Analyze a KakaoTalk .ktheme package for internal consistency.

This does NOT invent Kakao's official "required" list (that ships in their
spec). Instead it reports facts and self-consistency problems we can verify:

  * is KakaoTalkTheme.css present at the archive root?
  * every Images/*.png referenced by the CSS -- does it exist in the zip?
  * for each base image, are the @2x / @3x Retina variants present?
  * which packaged images are never referenced (orphans)?
  * the CSS blocks (selectors) and the color palette in use.

Usage:  python3 scripts/analyze_theme.py dist/PastelBunny.ktheme
"""

import sys
import re
import zipfile
from collections import defaultdict

CSS_NAME = "KakaoTalkTheme.css"


def main(path):
    try:
        zf = zipfile.ZipFile(path)
    except Exception as e:
        print(f"ERROR: cannot open {path}: {e}")
        return 1

    names = [n for n in zf.namelist() if not n.endswith("/")]
    issues, warnings = [], []

    print(f"\n=== Analyzing {path} ===")
    print(f"Files in package: {len(names)}")

    # 1) stylesheet present at root?
    if CSS_NAME not in names:
        found = [n for n in names if n.lower().endswith(".css")]
        issues.append(f"Missing {CSS_NAME} at root. CSS files found: {found or 'none'}")
        css = ""
    else:
        css = zf.read(CSS_NAME).decode("utf-8", "replace")
        print(f"Stylesheet: {CSS_NAME}  (OK)")

    # 2) CSS blocks (selectors)
    blocks = re.findall(r"([A-Za-z][\w]*)\s*\{", css)
    print(f"CSS blocks: {len(blocks)}")
    for b in blocks:
        print(f"    - {b}")

    # 3) colors
    colors = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}", css)))
    print(f"Unique colors: {len(colors)}")
    print("    " + "  ".join(colors))
    if len(colors) > 20:
        warnings.append(f"{len(colors)} colors (over 20) -- harder to maintain")

    # 4) referenced images exist?
    refs = sorted(set(re.findall(r"url\(\s*([^)]+?)\s*\)", css)))
    pkg = set(names)
    print(f"\nImages referenced by CSS: {len(refs)}")
    for r in refs:
        ok = r in pkg
        mark = "OK " if ok else "MISSING"
        print(f"    [{mark}] {r}")
        if not ok:
            issues.append(f"CSS references '{r}' but it is not in the package")

    # 5) retina coverage for every packaged image
    imgs = [n for n in names if n.lower().endswith(".png")]
    print(f"\nPackaged PNGs: {len(imgs)}")
    bases = defaultdict(set)  # base -> {'', '@2x', '@3x'}
    for n in imgs:
        m = re.match(r"(.*?)(@2x|@3x)?\.png$", n)
        base, scale = m.group(1), m.group(2) or ""
        bases[base].add(scale)
    for base, scales in sorted(bases.items()):
        missing = {"", "@2x", "@3x"} - scales
        if missing:
            human = ", ".join(s or "@1x" for s in sorted(missing))
            warnings.append(f"{base}.png missing variant(s): {human}")

    # 6) orphan images (packaged but never referenced)
    #    backgrounds/bubbles/tab icons may be referenced by name-convention
    #    rather than url(), so treat as info only.
    referenced_files = set(refs)
    orphans = [n for n in imgs if n not in referenced_files]
    if orphans:
        print(f"\nNot directly referenced via url() ({len(orphans)}) -- "
              f"may be used by naming convention:")
        for o in sorted(orphans)[:60]:
            print(f"    - {o}")

    # ---- summary ----
    print("\n=== Summary ===")
    if issues:
        print(f"ISSUES ({len(issues)}):")
        for i in issues:
            print(f"  X {i}")
    else:
        print("ISSUES: none")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("WARNINGS: none")
    print()
    return 1 if issues else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/analyze_theme.py <file.ktheme>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
