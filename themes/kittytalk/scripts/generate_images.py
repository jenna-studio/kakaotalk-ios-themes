#!/usr/bin/env python3
"""
Generate every PNG asset for the "KittyTalk" KakaoTalk iOS theme.

This theme is built from the user's own Hello Kitty artwork, NOT redrawn:
  * assets/source/kitty_face.png    -> profiles, theme icon, passcode hero
  * assets/source/kitty_bubble.jpg  -> chat bubbles (and the bow cropped from it
                                       is reused for tab icons, passcode bullets
                                       and the faint background pattern)

Pipeline:
  * the bubble JPEG's light-blue background is flood-filled to transparent
  * the receiver bubble is the bubble as-is (red bow, top-right, tail bottom-left)
  * the sender bubble is mirrored (tail bottom-right) and its bow recoloured to
    burgundy, so the two read as one design system but are easy to tell apart
  * bubbles ship as 9-slice art; the cap is measured from the bow/tail so the
    bow never distorts when KakaoTalk stretches the bubble

Conventions from the official KakaoTalk 8.0.0 iOS Theme guide:
  * Images are 2x-based:  name.png == name@2x.png (2x px),  name@3x.png (3x px)
  * Insets/caps in the CSS are 1x-based

Run: python3 themes/kittytalk/scripts/generate_images.py
"""

import os
import random
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "Images")
PREV = os.path.join(ROOT, "preview")
SRC = os.path.join(ROOT, "assets", "source")
FONTS = os.path.join(ROOT, "assets", "fonts")
os.makedirs(IMG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

# ---- palette --------------------------------------------------------------
WHITE    = (255, 255, 255)
RED      = (230, 0, 45)        # #E6002D
BURGUNDY = (150, 14, 38)       # sender bow
BLACK    = (17, 17, 17)
LGRAY    = (246, 246, 246)
PATTERN  = (255, 158, 182)     # faint background tint (low alpha)


def save_img(img, name):
    img.save(os.path.join(IMG, name))


def trim(img):
    bb = img.split()[-1].getbbox()
    return img.crop(bb) if bb else img


# ===========================================================================
# Load + clean the source artwork
# ===========================================================================
def load_face():
    return trim(Image.open(os.path.join(SRC, "kitty_face.png")).convert("RGBA"))


def load_bubble():
    """Open the bubble JPEG and flood-fill the light-blue background away."""
    b = Image.open(os.path.join(SRC, "kitty_bubble.jpg")).convert("RGB")
    w, h = b.size
    rgba = b.convert("RGBA")
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for s in seeds:
        ImageDraw.floodfill(rgba, s, (255, 0, 255, 0), thresh=62)
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            r, g, bl, a = px[x, y]
            if (r, g, bl) == (255, 0, 255):
                px[x, y] = (0, 0, 0, 0)
            elif bl > 175 and bl - r > 28 and g > 165:   # stray blue fringe
                px[x, y] = (0, 0, 0, 0)
    return trim(rgba)


def recolor_red_to(img, target):
    """Map the red bow pixels to `target`, keep black outline / white intact."""
    out = img.copy()
    px = out.load()
    w, h = out.size
    tr, tg, tb = target
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and r > 120 and g < 130 and b < 130 and r - max(g, b) > 40:
                # scale brightness of the red onto the target hue
                f = r / 230.0
                px[x, y] = (int(tr * f), int(tg * f), int(tb * f), a)
    return out


def crop_bow(bubble):
    """Bounding box of the red bow in the (receiver) bubble, + margin."""
    px = bubble.load()
    w, h = bubble.size
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 120 and r > 150 and g < 120 and b < 120:
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    mx = int((maxx - minx) * 0.16)
    my = int((maxy - miny) * 0.16)
    box = (max(0, minx - mx), max(0, miny - my),
           min(w, maxx + mx), min(h, maxy + my))
    crop = bubble.crop(box)
    # the bow is only red + black outline -- drop the white bubble-body remnant
    cp = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = cp[x, y]
            if a and min(r, g, b) > 188:        # near-white -> transparent
                cp[x, y] = (r, g, b, 0)
    return trim(crop)


FACE = load_face()
BUBBLE = load_bubble()
BOW = crop_bow(BUBBLE)
BOW_BURG = recolor_red_to(BOW, BURGUNDY)


# ===========================================================================
# Helpers
# ===========================================================================
def fit_circle(img, size, scale=0.92):
    """Scale `img` to sit inside a circle of diameter `size`, centered."""
    im = img.copy()
    im.thumbnail((int(size * scale), int(size * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas


def fit(img, w, h, scale=1.0):
    im = img.copy()
    im.thumbnail((int(w * scale), int(h * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return canvas


# ===========================================================================
# Chat bubbles (real artwork, 9-slice; cap measured from the bow/tail)
# ===========================================================================
print("bubbles...")
# Canonical bubble size (@3x). Receiver = real bubble; sender = mirrored + burgundy.
BUB3_W = 192
scale3 = BUB3_W / BUBBLE.width
BUB3_H = int(BUBBLE.height * scale3)
recv3 = BUBBLE.resize((BUB3_W, BUB3_H), Image.LANCZOS)
send_src = recolor_red_to(BUBBLE, BURGUNDY).transpose(Image.FLIP_LEFT_RIGHT)
send3 = send_src.resize((BUB3_W, BUB3_H), Image.LANCZOS)

# Measure the bow's bounding box, so the 9-slice cap fully contains it and the
# bow never distorts when KakaoTalk stretches the bubble's middle.
_p = BUBBLE.load()
bminx, bminy, bmaxx, bmaxy = BUBBLE.width, BUBBLE.height, 0, 0
for y in range(BUBBLE.height):
    for x in range(BUBBLE.width):
        r, g, b, a = _p[x, y]
        if a > 120 and r > 150 and g < 120 and b < 120:
            bminx = min(bminx, x); bmaxx = max(bmaxx, x)
            bminy = min(bminy, y); bmaxy = max(bmaxy, y)
# right cap must reach the bow's left edge; top cap must reach the bow's bottom.
cap_x_frac = min(0.46, (BUBBLE.width - bminx) / BUBBLE.width + 0.03)
cap_y_frac = min(0.46, bmaxy / BUBBLE.height + 0.03)
CAP1X = max(14, int(cap_x_frac * BUB3_W / 3))   # 1x px for the CSS
CAP1Y = max(14, int(cap_y_frac * BUB3_H / 3))

def write_bubble(prefix, art3):
    two = art3.resize((BUB3_W * 2 // 3, BUB3_H * 2 // 3), Image.LANCZOS)
    sel = Image.eval(art3, lambda v: v)  # placeholder (kept identical alpha)
    # selected = same art on a faint gray plate so a pressed bubble reads
    plate = Image.new("RGBA", art3.size, (0, 0, 0, 0))
    selected3 = Image.alpha_composite(plate, art3)
    sel2 = selected3.resize(two.size, Image.LANCZOS)
    for v in ("01", "02"):
        save_img(two, f"{prefix}{v}.png")
        save_img(two, f"{prefix}{v}@2x.png")
        save_img(art3, f"{prefix}{v}@3x.png")
        save_img(sel2, f"{prefix}{v}Selected.png")
        save_img(sel2, f"{prefix}{v}Selected@2x.png")
        save_img(selected3, f"{prefix}{v}Selected@3x.png")

write_bubble("chatroomBubbleReceive", recv3)
write_bubble("chatroomBubbleSend", send3)


# ===========================================================================
# Backgrounds -- white with a tiny, faint repeating bow pattern (real bow)
# ===========================================================================
print("backgrounds...")
def bow_pattern_bg(size, seed=7, alpha=24, scale=1.0):
    w, h = size
    base = Image.new("RGBA", (w, h), WHITE + (255,))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rnd = random.Random(seed)
    unit = max(40, int(min(w, h) / 7 * scale))
    stamp = BOW.copy()
    stamp.thumbnail((int(unit * 0.5), int(unit * 0.5)), Image.LANCZOS)
    # tint the stamp a soft pink + low alpha
    sp = stamp.load()
    for y in range(stamp.height):
        for x in range(stamp.width):
            r, g, b, a = sp[x, y]
            if a:
                sp[x, y] = PATTERN + (int(a / 255 * alpha),)
    row, y = 0, -unit // 2
    while y < h + unit:
        x = -unit // 2 + (unit // 2 if row % 2 else 0)
        while x < w + unit:
            jx = rnd.randint(-unit // 7, unit // 7)
            jy = rnd.randint(-unit // 7, unit // 7)
            b = stamp.rotate(rnd.choice((-12, 0, 12)), expand=True, resample=Image.BICUBIC)
            layer.alpha_composite(b, (x + jx, y + jy))
            x += unit
        y += unit
        row += 1
    return Image.alpha_composite(base, layer).convert("RGB")

chat = bow_pattern_bg((846, 1503), seed=11, alpha=22)
save_img(chat, "chatroomBgImage@2x.png"); save_img(chat, "chatroomBgImage@3x.png")
main = bow_pattern_bg((846, 1503), seed=5, alpha=20)
save_img(main, "mainBgImage@2x.png"); save_img(main, "mainBgImage@3x.png")
save_img(Image.new("RGB", (750, 106), WHITE), "maintabBgImage@2x.png")
save_img(Image.new("RGB", (1125, 159), WHITE), "maintabBgImage@3x.png")


# ===========================================================================
# Tab icons -- the real bow.  normal = soft grey, selected = red.
# ===========================================================================
print("tab icons...")
def grey_bow(img):
    out = img.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                lum = int(0.3 * r + 0.6 * g + 0.1 * b)
                lum = int(120 + (lum - 120) * 0.4)        # flatten toward mid-grey
                px[x, y] = (lum, lum, lum, a)
    return out

BOW_GREY = grey_bow(BOW)
def tab_icon(w, h, art):
    return fit(art, w, h, scale=0.74)

TAB_SLOTS = ["Friends", "Chats", "Browse", "Find", "Piccoma", "Game", "More"]
for slot in TAB_SLOTS:
    name = f"maintabIco{slot}"
    tab_icon(76, 58, BOW_GREY).save(os.path.join(IMG, f"{name}@2x.png"))
    tab_icon(156, 118, BOW_GREY).save(os.path.join(IMG, f"{name}@3x.png"))
    tab_icon(76, 58, BOW).save(os.path.join(IMG, f"{name}Selected@2x.png"))
    tab_icon(156, 118, BOW).save(os.path.join(IMG, f"{name}Selected@3x.png"))


# ===========================================================================
# Theme icon, profiles, add-friend (real face)
# ===========================================================================
print("icons & profiles...")
fit(FACE, 162, 162, scale=0.96).save(os.path.join(IMG, "commonIcoTheme.png"))
for name in ("profileImg01", "profileImg02", "profileImg03"):
    f = fit_circle(FACE, 240)
    f.save(os.path.join(IMG, f"{name}@2x.png"))
    f.save(os.path.join(IMG, f"{name}@3x.png"))

def add_friend(w, h):
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bow = BOW.copy(); bow.thumbnail((int(w * 0.62), int(h * 0.78)), Image.LANCZOS)
    canvas.alpha_composite(bow, (int(w * 0.02), (h - bow.height) // 2))
    d = ImageDraw.Draw(canvas)
    cx, cy, r = int(w * 0.82), int(h * 0.30), int(h * 0.16)
    lw = max(2, int(h * 0.085))
    d.line([cx - r, cy, cx + r, cy], fill=RED, width=lw)
    d.line([cx, cy - r, cx, cy + r], fill=RED, width=lw)
    return canvas
add_friend(84, 68).save(os.path.join(IMG, "findBtnAddFriend@2x.png"))
add_friend(126, 102).save(os.path.join(IMG, "findBtnAddFriend@3x.png"))


# ===========================================================================
# Passcode -- white bg + faint bows + kitty hero; bullets = real bow
# ===========================================================================
print("passcode...")
def passcode_bg(size):
    bg = bow_pattern_bg((size, size), seed=3, alpha=18, scale=1.1).convert("RGBA")
    hero = fit(FACE, int(size * 0.20), int(size * 0.20), scale=1.0)
    bg.alpha_composite(hero, ((size - hero.width) // 2, int(size * 0.11)))
    return bg.convert("RGB")
pbg = passcode_bg(846)
pbg.resize((375, 375), Image.LANCZOS).save(os.path.join(IMG, "passcodeBgImage.png"))
pbg.save(os.path.join(IMG, "passcodeBgImage@2x.png"))
pbg.save(os.path.join(IMG, "passcodeBgImage@3x.png"))

def bullet(px, filled):
    art = BOW if filled else BOW_GREY
    b = fit(art, px, int(px * 0.8), scale=0.9)
    if not filled:                      # fade the empty state
        a = b.split()[-1].point(lambda v: int(v * 0.5))
        b.putalpha(a)
    return b
for i in (1, 2, 3, 4):
    for suf in ("@2x", "@3x"):
        bullet(132, False).save(os.path.join(IMG, f"passcodeImgCode0{i}{suf}.png"))
        bullet(132, True).save(os.path.join(IMG, f"passcodeImgCode0{i}Selected{suf}.png"))

def keypad(px):
    im = Image.new("RGBA", (px * 4, px * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([int(px * 4 * 0.08)] * 2 + [int(px * 4 * 0.92)] * 2,
                               fill=LGRAY + (255,))
    return im.resize((px, px), Image.LANCZOS)
keypad(90).save(os.path.join(IMG, "passcodeKeypadPressed.png"))
keypad(120).save(os.path.join(IMG, "passcodeKeypadPressed@2x.png"))
keypad(180).save(os.path.join(IMG, "passcodeKeypadPressed@3x.png"))


# ===========================================================================
# Preview + stretch proof (NOT shipped inside the .ktheme)
# ===========================================================================
print("preview...")
from PIL import ImageFont

def font(p, sz):
    try:
        return ImageFont.truetype(os.path.join(FONTS, p), sz)
    except Exception:
        return ImageFont.load_default()

def nine_slice(img, capx, capy, tw, th):
    w, h = img.size
    cx = min(capx, w // 2 - 1)
    cy = min(capy, h // 2 - 1)
    tw, th = max(tw, 2 * cx + 1), max(th, 2 * cy + 1)
    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    xs = [(0, cx, 0, cx), (cx, w - cx, cx, tw - cx), (w - cx, w, tw - cx, tw)]
    ys = [(0, cy, 0, cy), (cy, h - cy, cy, th - cy), (h - cy, h, th - cy, th)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 <= sx0 or sy1 <= sy0:
                continue
            tile = img.crop((sx0, sy0, sx1, sy1))
            out.alpha_composite(tile.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)),
                                            Image.BICUBIC), (dx0, dy0))
    return out

cap3x = int(CAP1X * 3)
cap3y = int(CAP1Y * 3)

# (a) stretch proof
verify = Image.new("RGBA", (820, 300), WHITE + (255,))
for i, (w, h) in enumerate([(BUB3_W, BUB3_H), (260, BUB3_H), (260, 150), (150, 150)]):
    verify.alpha_composite(nine_slice(recv3, cap3x, cap3y, w, h), (12 + i * 200, 20))
verify.convert("RGB").save(os.path.join(PREV, "verify_stretch.png"))

# (b) chat mockup
PW, PH = 414, 736
mock = bow_pattern_bg((PW, PH), seed=11, alpha=22).convert("RGBA")
md = ImageDraw.Draw(mock)
f_logo = font("Fredoka.ttf", 22)
f_body = font("Quicksand.ttf", 15)
f_sub = font("Quicksand.ttf", 12)

md.rectangle([0, 0, PW, 54], fill=WHITE)
md.line([0, 54, PW, 54], fill=(232, 232, 232), width=1)
lb = BOW.copy(); lb.thumbnail((30, 22), Image.LANCZOS)
mock.alpha_composite(lb, (PW // 2 - 78, 16))
md.text((PW // 2 - 44, 27), "KittyTalk", font=f_logo, fill=BLACK, anchor="lm")

def msg(text, side, y):
    tw = int(md.textlength(text, font=f_body))
    bw = max(70, tw + 54)
    bh = 56
    art = recv3 if side == "L" else send3
    b = nine_slice(art, cap3x, cap3y, int(bw / 0.5), int(bh / 0.5))
    b = b.resize((bw, int(b.height * 0.5)), Image.LANCZOS)
    if side == "L":
        face = fit_circle(FACE, 34)
        mock.alpha_composite(face, (12, y + 6))
        x = 52
        tx = x + b.width // 2 - 6
    else:
        x = PW - 14 - b.width
        tx = x + b.width // 2 + 6
    mock.alpha_composite(b, (x, y))
    md.text((tx, y + b.height // 2), text, font=f_body, fill=BLACK, anchor="mm")

msg("hi! did you see the new theme?", "L", 86)
msg("yes!! so clean and cute", "R", 188)
msg("real kitty vibes now", "L", 290)

TBH = 60
md.rectangle([0, PH - TBH, PW, PH], fill=WHITE)
md.line([0, PH - TBH, PW, PH - TBH], fill=(232, 232, 232), width=1)
tabs = [("Friends", True), ("Chats", False), ("Open Chat", False),
        ("Shopping", False), ("More", False)]
slot = PW // len(tabs)
for i, (lab, on) in enumerate(tabs):
    icon = BOW if on else BOW_GREY
    ic = icon.copy(); ic.thumbnail((30, 22), Image.LANCZOS)
    mock.alpha_composite(ic, (i * slot + (slot - ic.width) // 2, PH - TBH + 9))
    md.text((i * slot + slot // 2, PH - 14), lab, font=f_sub,
            fill=RED if on else BLACK, anchor="mm")

mock.convert("RGB").save(os.path.join(PREV, "preview.png"))
fit(FACE, 180, 180, scale=0.96).save(os.path.join(PREV, "thumbnail.png"))
print("done.  cap(1x) = %dx%d" % (CAP1X, CAP1Y))
