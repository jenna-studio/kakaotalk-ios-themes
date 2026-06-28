#!/usr/bin/env python3
"""
Generate every PNG asset for the "KittyTalk" KakaoTalk iOS theme.

Design language (a minimal Sanrio x Apple look):
  * predominantly WHITE, generous whitespace, flat
  * BLACK outlines and typography (#111111 / #1F1F1F)
  * RED is the only accent (#E6002D) -- Hello Kitty ribbon red
  * the recurring motif is a little BOW (ribbon), never hearts or stars
  * receiver bubbles wear a red bow; sender bubbles a burgundy bow, so the two
    read as the same design system but are easy to tell apart
  * backgrounds are white with a tiny, very faint repeating bow pattern

Conventions from the official KakaoTalk 8.0.0 iOS Theme guide:
  * Images are 2x-based:  name.png == name@2x.png (2x px),  name@3x.png (3x px)
  * Insets/caps in the CSS are 1x-based
  * Chat bubbles are 9-slice stretched with a `20px 20px` cap (1x); the bow sits
    in the bubble's TOP-RIGHT corner, inside that cap, so it never distorts.

Run: python3 themes/kittytalk/scripts/generate_images.py
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "Images")
PREV = os.path.join(ROOT, "preview")
FONTS = os.path.join(ROOT, "assets", "fonts")
os.makedirs(IMG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

DS = 12  # internal draw units per 1x point (downscaled later -> crisp)

# ---- palette --------------------------------------------------------------
WHITE      = (255, 255, 255)
RED        = (230, 0, 45)        # #E6002D  Hello Kitty red (receiver bow, accent)
BURGUNDY   = (150, 14, 38)       # sender bow -- same family, clearly different
BLACK      = (17, 17, 17)        # #111111  typography
OUTLINE    = (31, 31, 31)        # #1F1F1F  outlines
LGRAY      = (246, 246, 246)     # #F6F6F6  pressed / secondary surfaces
GRAY_TXT   = (138, 138, 142)     # muted status text
NOSE       = (255, 198, 0)       # kitty nose
PATTERN    = (255, 158, 182)     # faint background bow tint (used at low alpha)


def font(path, sz):
    try:
        return ImageFont.truetype(os.path.join(FONTS, path), sz)
    except Exception:
        return ImageFont.load_default()


def save_img(img, path):
    img.save(os.path.join(IMG, path))


def darken(c, f=0.90):
    return tuple(max(0, int(v * f)) for v in c[:3]) + tuple(c[3:])


# ===========================================================================
# The bow (ribbon) -- the theme's one recurring shape.
# Two bulged loops flanking a small rounded knot.  Returns an RGBA image.
# ===========================================================================
def make_bow(w, h, fill, outline=OUTLINE, ow=None):
    s = 4
    W, H = w * s, h * s
    if ow is None:
        ow = max(1.0, w * 0.07)
    owp = int(ow * s)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2.0, H / 2.0
    half_w = W * 0.5 - owp
    half_h = H * 0.5 - owp
    knot_hw, knot_hh = W * 0.11, H * 0.32
    inner = knot_hw * 0.5

    left = [(cx - inner, cy),
            (cx - half_w, cy - half_h),
            (cx - half_w * 1.04, cy),
            (cx - half_w, cy + half_h)]
    right = [(cx + inner, cy),
             (cx + half_w, cy - half_h),
             (cx + half_w * 1.04, cy),
             (cx + half_w, cy + half_h)]

    d.polygon(left, fill=fill)
    d.polygon(right, fill=fill)
    if outline is not None and owp > 0:
        d.line(left + [left[0]], fill=outline, width=owp, joint="curve")
        d.line(right + [right[0]], fill=outline, width=owp, joint="curve")
    d.rounded_rectangle([cx - knot_hw, cy - knot_hh, cx + knot_hw, cy + knot_hh],
                        radius=knot_hw, fill=fill,
                        outline=outline if outline is not None else None,
                        width=owp if outline is not None else 0)
    return im.resize((w, h), Image.LANCZOS)


# ===========================================================================
# Hello Kitty face -- white, black outline, red bow, black eyes, gold nose.
# Used for profile images, the theme icon, and the passcode hero.
# ===========================================================================
def kitty_face(size, bow_side="right", bow_fill=RED):
    s = 4
    W = size * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ow = max(2, int(W * 0.020))

    fw, fh = W * 0.72, W * 0.58
    fcx, fcy = W * 0.5, W * 0.55
    fx0, fy0, fx1, fy1 = fcx - fw / 2, fcy - fh / 2, fcx + fw / 2, fcy + fh / 2

    # ears (pointed), drawn first so the face covers their inner base
    earL = [(fcx - fw * 0.40, fcy - fh * 0.18),
            (fcx - fw * 0.50, fcy - fh * 0.86),
            (fcx - fw * 0.04, fcy - fh * 0.40)]
    earR = [(fcx + fw * 0.40, fcy - fh * 0.18),
            (fcx + fw * 0.50, fcy - fh * 0.86),
            (fcx + fw * 0.04, fcy - fh * 0.40)]
    for ear in (earL, earR):
        d.polygon(ear, fill=WHITE)
        d.line(ear + [ear[0]], fill=OUTLINE, width=ow, joint="curve")

    # face
    d.ellipse([fx0, fy0, fx1, fy1], fill=WHITE, outline=OUTLINE, width=ow)

    # whiskers (three each side, starting at the cheek, fanning out)
    wlw = max(2, int(W * 0.013))
    for sx in (-1, 1):
        bx = fcx + sx * fw * 0.40
        for k, dy in enumerate((-1, 0, 1)):
            y = fcy + fh * 0.02 + dy * fh * 0.13
            ex = fcx + sx * fw * 0.66
            ey = y + dy * fh * 0.10
            d.line([(bx, y), (ex, ey)], fill=OUTLINE, width=wlw)

    # eyes
    for sx in (-1, 1):
        ex = fcx + sx * fw * 0.23
        ey = fcy + fh * 0.04
        d.ellipse([ex - W * 0.030, ey - W * 0.050, ex + W * 0.030, ey + W * 0.050],
                  fill=BLACK)
    # nose
    d.ellipse([fcx - W * 0.028, fcy + fh * 0.16, fcx + W * 0.028, fcy + fh * 0.27],
              fill=NOSE)

    # bow on one ear
    sx = 1 if bow_side == "right" else -1
    bw, bh = int(W * 0.34), int(W * 0.24)
    bow = make_bow(bw, bh, bow_fill, OUTLINE, ow=W * 0.022)
    bx = fcx + sx * fw * 0.40
    by = fcy - fh * 0.46
    im.alpha_composite(bow, (int(bx - bw / 2), int(by - bh / 2)))

    return im.resize((size, size), Image.LANCZOS)


# ===========================================================================
# Chat bubbles  (1x = 52 x 54 ; bow in the top-right corner inside the 20px cap)
# ===========================================================================
BUB_W, BUB_H = 52, 54

def _bubble_master(bow_fill, body_fill=WHITE):
    W, H = BUB_W * DS, BUB_H * DS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(2, int(2.2 * DS))
    body = [2 * DS, 12 * DS, W - 2 * DS, H - 2 * DS]
    r = 15 * DS
    d.rounded_rectangle(body, radius=r, fill=body_fill, outline=OUTLINE, width=lw)

    # bow tucked into the top-right corner, fully within the 20px (1x) cap
    bw, bh = int(18 * DS), int(12 * DS)
    bow = make_bow(bw, bh, bow_fill, OUTLINE, ow=2.0 * DS)
    bx_right = W - int(1.5 * DS)
    by_center = int(9 * DS)
    im.alpha_composite(bow, (bx_right - bw, by_center - bh // 2))
    return im


def write_bubble(prefix, bow_fill):
    normal = _bubble_master(bow_fill, WHITE)
    sel = _bubble_master(darken(bow_fill, 0.85), (240, 240, 240))
    two = (BUB_W * 2, BUB_H * 2)
    three = (BUB_W * 3, BUB_H * 3)
    for variant in ("01", "02"):                 # 01 and 02 share artwork
        n2 = normal.resize(two, Image.LANCZOS)
        n3 = normal.resize(three, Image.LANCZOS)
        s2 = sel.resize(two, Image.LANCZOS)
        s3 = sel.resize(three, Image.LANCZOS)
        save_img(n2, f"{prefix}{variant}.png")
        save_img(n2, f"{prefix}{variant}@2x.png")
        save_img(n3, f"{prefix}{variant}@3x.png")
        save_img(s2, f"{prefix}{variant}Selected.png")
        save_img(s2, f"{prefix}{variant}Selected@2x.png")
        save_img(s3, f"{prefix}{variant}Selected@3x.png")


print("bubbles...")
write_bubble("chatroomBubbleReceive", RED)
write_bubble("chatroomBubbleSend", BURGUNDY)


# ===========================================================================
# Backgrounds -- white with a tiny, faint, repeating bow pattern
# ===========================================================================
def bow_pattern_bg(size, seed=7, alpha=30, scale=1.0):
    w, h = size
    base = Image.new("RGBA", (w, h), WHITE + (255,))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rnd = random.Random(seed)
    unit = max(20, int(min(w, h) / 7 * scale))      # grid spacing
    bw = int(unit * 0.46)
    bh = int(bw * 0.66)
    stamp = make_bow(bw, bh, PATTERN + (alpha,), outline=None)
    row = 0
    y = -unit // 2
    while y < h + unit:
        x = -unit // 2 + (unit // 2 if row % 2 else 0)
        while x < w + unit:
            jx = rnd.randint(-unit // 7, unit // 7)
            jy = rnd.randint(-unit // 7, unit // 7)
            ang = rnd.choice((-14, -7, 0, 7, 14))
            b = stamp.rotate(ang, expand=True, resample=Image.BICUBIC)
            layer.alpha_composite(b, (x + jx, y + jy))
            x += unit
        y += unit
        row += 1
    return Image.alpha_composite(base, layer).convert("RGB")


print("backgrounds...")
chat = bow_pattern_bg((846, 1503), seed=11, alpha=26)
save_img(chat, "chatroomBgImage@2x.png"); save_img(chat, "chatroomBgImage@3x.png")
main = bow_pattern_bg((846, 1503), seed=5, alpha=22)
save_img(main, "mainBgImage@2x.png"); save_img(main, "mainBgImage@3x.png")

# Tab bar: flat white
def solid(size, color):
    return Image.new("RGB", size, color)
save_img(solid((750, 106), WHITE), "maintabBgImage@2x.png")
save_img(solid((1125, 159), WHITE), "maintabBgImage@3x.png")


# ===========================================================================
# Tab icons -- every tab is a bow.  normal = black outline, selected = red.
# 2x:76x58   3x:156x118
# ===========================================================================
print("tab icons...")
def tab_bow(w, h, selected):
    fill = RED if selected else WHITE
    bw = int(w * 0.62)
    bh = int(bw * 0.66)
    bow = make_bow(bw, bh, fill, OUTLINE, ow=max(1.5, w * 0.028))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(bow, ((w - bw) // 2, (h - bh) // 2))
    return im

TAB_SLOTS = ["Friends", "Chats", "Browse", "Find", "Piccoma", "Game", "More"]
for slot in TAB_SLOTS:
    name = f"maintabIco{slot}"
    tab_bow(76, 58, False).save(os.path.join(IMG, f"{name}@2x.png"))
    tab_bow(156, 118, False).save(os.path.join(IMG, f"{name}@3x.png"))
    tab_bow(76, 58, True).save(os.path.join(IMG, f"{name}Selected@2x.png"))
    tab_bow(156, 118, True).save(os.path.join(IMG, f"{name}Selected@3x.png"))


# ===========================================================================
# Theme icon, profile images, add-friend button
# ===========================================================================
print("icons & profiles...")
kitty_face(162).save(os.path.join(IMG, "commonIcoTheme.png"))

# three profile variants (bow side / colour) so the list has variety
PROFILES = [
    ("profileImg01", "right", RED),
    ("profileImg02", "left",  RED),
    ("profileImg03", "right", BURGUNDY),
]
for name, side, col in PROFILES:
    f = kitty_face(240, bow_side=side, bow_fill=col)
    f.save(os.path.join(IMG, f"{name}@2x.png"))
    f.save(os.path.join(IMG, f"{name}@3x.png"))

def add_friend(w, h):
    s = 4
    W, H = w * s, h * s
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bw = int(W * 0.62)
    bh = int(bw * 0.66)
    bow = make_bow(bw, bh, RED, OUTLINE, ow=max(2, W * 0.02))
    im.alpha_composite(bow, (int(W * 0.04), (H - bh) // 2))
    # small plus, top-right
    cx, cy, r = int(W * 0.80), int(H * 0.30), int(H * 0.16)
    lw = int(H * 0.085)
    d.line([cx - r, cy, cx + r, cy], fill=RED, width=lw)
    d.line([cx, cy - r, cx, cy + r], fill=RED, width=lw)
    return im.resize((w, h), Image.LANCZOS)
add_friend(84, 68).save(os.path.join(IMG, "findBtnAddFriend@2x.png"))
add_friend(126, 102).save(os.path.join(IMG, "findBtnAddFriend@3x.png"))


# ===========================================================================
# Passcode -- white bg + faint bows + a kitty hero; bullets become bows.
# ===========================================================================
print("passcode...")
def passcode_bg(size):
    bg = bow_pattern_bg((size, size), seed=3, alpha=20, scale=1.1).convert("RGBA")
    hero = int(size * 0.17)
    face = kitty_face(hero)
    bg.alpha_composite(face, ((size - hero) // 2, int(size * 0.13)))
    return bg.convert("RGB")
pbg = passcode_bg(846)
pbg.resize((375, 375), Image.LANCZOS).save(os.path.join(IMG, "passcodeBgImage.png"))
pbg.save(os.path.join(IMG, "passcodeBgImage@2x.png"))
pbg.save(os.path.join(IMG, "passcodeBgImage@3x.png"))

def passcode_bullet(px, filled):
    # empty = faint black-outline bow; entered = solid red bow
    if filled:
        return make_bow(px, int(px * 0.7), RED, OUTLINE, ow=px * 0.05)
    return make_bow(px, int(px * 0.7), (255, 255, 255, 0), outline=(180, 180, 184),
                    ow=px * 0.045)

for i in (1, 2, 3, 4):
    for suf in ("@2x", "@3x"):
        passcode_bullet(132, False).save(os.path.join(IMG, f"passcodeImgCode0{i}{suf}.png"))
        passcode_bullet(132, True).save(os.path.join(IMG, f"passcodeImgCode0{i}Selected{suf}.png"))

def keypad(px):
    s = 4
    W = px * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([int(W * 0.08)] * 2 + [int(W * 0.92)] * 2,
                               fill=LGRAY + (255,))
    return im.resize((px, px), Image.LANCZOS)
keypad(90).save(os.path.join(IMG, "passcodeKeypadPressed.png"))
keypad(120).save(os.path.join(IMG, "passcodeKeypadPressed@2x.png"))
keypad(180).save(os.path.join(IMG, "passcodeKeypadPressed@3x.png"))


# ===========================================================================
# Verification + preview (NOT shipped inside the .ktheme)
# ===========================================================================
print("preview...")
def nine_slice(img, cap, tw, th):
    w, h = img.size
    c = min(cap, w // 2 - 1, h // 2 - 1)
    tw, th = max(tw, 2 * c + 1), max(th, 2 * c + 1)
    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    xs = [(0, c, 0, c), (c, w - c, c, tw - c), (w - c, w, tw - c, tw)]
    ys = [(0, c, 0, c), (c, h - c, c, th - c), (h - c, h, th - c, th)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 <= sx0 or sy1 <= sy0:
                continue
            tile = img.crop((sx0, sy0, sx1, sy1))
            out.alpha_composite(tile.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)),
                                            Image.BICUBIC), (dx0, dy0))
    return out

recv3 = _bubble_master(RED).resize((BUB_W * 3, BUB_H * 3), Image.LANCZOS)
send3 = _bubble_master(BURGUNDY).resize((BUB_W * 3, BUB_H * 3), Image.LANCZOS)
cap3 = 20 * 3

# (a) stretch proof -- bow must stay crisp in the top-right corner at any size
verify = Image.new("RGBA", (760, 280), WHITE + (255,))
for i, (w, h) in enumerate([(BUB_W * 3, BUB_H * 3), (430, BUB_H * 3), (430, 240), (190, 240)]):
    verify.alpha_composite(nine_slice(recv3, cap3, w, h), (10 + i * 185, 20))
verify.convert("RGB").save(os.path.join(PREV, "verify_stretch.png"))

# (b) chat mockup (uses the cute rounded font for everything we render)
PW, PH = 414, 736
mock = bow_pattern_bg((PW, PH), seed=11, alpha=24).convert("RGBA")
md = ImageDraw.Draw(mock)
f_logo = font("Fredoka.ttf", 22)
f_name = font("Fredoka.ttf", 16)
f_body = font("Quicksand.ttf", 15)
f_sub = font("Quicksand.ttf", 12)

# header
md.rectangle([0, 0, PW, 54], fill=WHITE)
md.line([0, 54, PW, 54], fill=(232, 232, 232), width=1)
logo_bow = make_bow(26, 18, RED, OUTLINE, ow=1.6)
mock.alpha_composite(logo_bow, (PW // 2 - 78, 18))
md.text((PW // 2 - 44, 27), "KittyTalk", font=f_logo, fill=BLACK, anchor="lm")

def msg(text, side, y):
    tw_text = int(md.textlength(text, font=f_body))
    bw = tw_text + 40            # text + horizontal padding
    bh = 40                      # single line height
    # build the bubble at 3x then downscale so the bow stays crisp
    b = nine_slice(recv3 if side == "L" else send3, cap3, int(bw / 0.5), int(bh / 0.5))
    b = b.resize((bw, bh + 8), Image.LANCZOS)
    if side == "L":
        face = kitty_face(34)
        mock.alpha_composite(face, (14, y + b.height - 30))
        x = 56
    else:
        x = PW - 16 - b.width
    mock.alpha_composite(b, (x, y))
    md.text((x + b.width // 2, y + b.height // 2), text, font=f_body,
            fill=BLACK, anchor="mm")

msg("hi! did you see the new theme?", "L", 92)
msg("yes!! so clean and cute", "R", 180)
msg("minimal kitty vibes", "L", 268)

# tab bar
TBH = 60
md.rectangle([0, PH - TBH, PW, PH], fill=WHITE)
md.line([0, PH - TBH, PW, PH - TBH], fill=(232, 232, 232), width=1)
tabs = [("Friends", True), ("Chats", False), ("Open Chat", False),
        ("Shopping", False), ("More", False)]
slot = PW // len(tabs)
for i, (lab, on) in enumerate(tabs):
    bw = 26
    bh = 18
    bow = make_bow(bw, bh, RED if on else WHITE, OUTLINE, ow=1.6)
    mock.alpha_composite(bow, (i * slot + (slot - bw) // 2, PH - TBH + 10))
    md.text((i * slot + slot // 2, PH - 14), lab, font=f_sub,
            fill=RED if on else BLACK, anchor="mm")

mock.convert("RGB").save(os.path.join(PREV, "preview.png"))
kitty_face(180).save(os.path.join(PREV, "thumbnail.png"))

print("done.")
