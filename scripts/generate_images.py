#!/usr/bin/env python3
"""
Generate every PNG asset for the "Pastel Bunny" KakaoTalk iOS theme,
following the official KakaoTalk 8.0.0 iOS Theme User Guide and matching
the asset names/sizes of a known-working theme.

Conventions from the guide:
  * Images are 2x-based:  name.png == name@2x.png (2x px),  name@3x.png (3x px)
  * Insets/caps in the CSS are 1x-based
  * Chat bubbles are 9-slice stretched with a `20px 20px` cap (1x). The two
    short bunny ears are placed in the bubble's TOP CORNERS, inside that cap,
    so they never distort when KakaoTalk stretches the bubble.

Run: python3 scripts/generate_images.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "theme", "Images")
PREV = os.path.join(ROOT, "preview")
os.makedirs(IMG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

DS = 12  # internal draw units per 1x point (downscaled later -> crisp)

# ---- pastel palette -------------------------------------------------------
PINK      = (255, 194, 219)
PINK_EAR  = (255, 167, 198)
PINK_LINE = (234, 146, 180)
MINT      = (184, 233, 214)
MINT_EAR  = (149, 212, 188)
MINT_LINE = (144, 201, 176)
BG_TOP    = (255, 244, 250)
BG_BOT    = (234, 246, 255)
PASS_TOP  = (255, 240, 248)
PASS_BOT  = (240, 248, 255)
TEXT_DARK = (92, 74, 84)
MUTED     = (190, 150, 168)
ACCENT    = (255, 111, 163)


def darken(c, f=0.86):
    return tuple(max(0, int(v * f)) for v in c)


def save_img(img, path):
    img.save(os.path.join(IMG, path))


# ===========================================================================
# Chat bubbles (1x = 52 x 54 ; ears in top corners inside the 20px cap)
# ===========================================================================
BUB_W, BUB_H = 52, 54  # 1x points

def _bubble_master(fill, ear, line):
    """Draw bunny bubble at DS resolution, return RGBA (DS*1x)."""
    W, H = BUB_W * DS, BUB_H * DS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = max(2, int(1.6 * DS))

    def ear_at(cx):
        ew, eh = 13 * DS, 18 * DS          # SHORT ears
        e = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
        ed = ImageDraw.Draw(e)
        ed.ellipse([0, 0, ew - 1, eh - 1], fill=fill, outline=line, width=lw)
        iw, ih = int(ew * 0.48), int(eh * 0.58)
        ed.ellipse([(ew - iw) // 2, int(eh * 0.24),
                    (ew - iw) // 2 + iw, int(eh * 0.24) + ih], fill=ear)
        im.alpha_composite(e, (int(cx * DS - ew / 2), 0))

    ear_at(12)   # left  (within 20px cap)
    ear_at(40)   # right (within 20px cap)

    body = [2 * DS, 12 * DS, W - 2 * DS, H - 2 * DS]
    r = 15 * DS
    d.rounded_rectangle(body, radius=r, fill=fill, outline=line, width=lw)
    d.rounded_rectangle([body[0] + lw, 12 * DS + lw, body[2] - lw, body[3] - lw],
                        radius=r, fill=fill)
    return im


def write_bubble(prefix, fill, ear, line):
    """Write 01/02 (+Selected), each as name.png(2x), @2x(2x), @3x(3x)."""
    normal = _bubble_master(fill, ear, line)
    sel = _bubble_master(darken(fill), darken(ear), darken(line))
    two = (BUB_W * 2, BUB_H * 2)
    three = (BUB_W * 3, BUB_H * 3)
    for variant in ("01", "02"):                     # 01 and 02 share art
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
write_bubble("chatroomBubbleSend", PINK, PINK_EAR, PINK_LINE)
write_bubble("chatroomBubbleReceive", MINT, MINT_EAR, MINT_LINE)


# ===========================================================================
# Backgrounds & patterns
# ===========================================================================
def gradient(size, top, bot):
    w, h = size
    col = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return col.resize((w, h))


def _bunny(d, x, y, s, c):
    d.ellipse([x - s, y - s, x + s, y + s], fill=c)
    for sx in (-1, 1):
        d.ellipse([x + sx * s // 2 - s // 4, y - 2 * s,
                   x + sx * s // 2 + s // 4, y - s // 2], fill=c)


def _heart(d, x, y, s, c):
    d.ellipse([x - s, y - s, x, y], fill=c)
    d.ellipse([x, y - s, x + s, y], fill=c)
    d.polygon([(x - s, y - s // 3), (x + s, y - s // 3), (x, y + s)], fill=c)


def _carrot(d, x, y, s, cc, lc):
    d.polygon([(x, y + 2 * s), (x - s, y - s // 2), (x + s, y - s // 2)], fill=cc)
    for o in (-0.4, 0, 0.4):
        d.ellipse([x + int(o * s) - s // 5, y - s, x + int(o * s) + s // 5, y], fill=lc)


def pattern_bg(size, density, top=BG_TOP, bot=BG_BOT, seed=11, amax=24):
    """Soft gradient with a FEW faint, small accents (kept subtle on purpose)."""
    import random
    random.seed(seed)
    img = gradient(size, top, bot).convert("RGBA")
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pal = [(255, 178, 205), (255, 196, 214), (188, 224, 255)]
    for _ in range(density):
        x, y = random.randint(0, w), random.randint(0, h)
        s = random.randint(max(5, w // 95), max(8, w // 60))   # smaller
        a = random.randint(max(6, amax - 12), amax)            # fainter
        if random.random() < 0.55:
            _heart(d, x, y, int(s * 0.9), random.choice(pal) + (a,))
        else:
            _bunny(d, x, y, s, random.choice(pal) + (a,))
    return Image.alpha_composite(img, layer).convert("RGB")


print("backgrounds...")
chat = pattern_bg((846, 1503), 24, seed=11, amax=22)
save_img(chat, "chatroomBgImage@2x.png"); save_img(chat, "chatroomBgImage@3x.png")
main = pattern_bg((846, 1503), 18, seed=5, amax=20)
save_img(main, "mainBgImage@2x.png"); save_img(main, "mainBgImage@3x.png")
passbg = pattern_bg((846, 846), 12, PASS_TOP, PASS_BOT, seed=3, amax=18)
save_img(passbg.resize((375, 375), Image.LANCZOS), "passcodeBgImage.png")
save_img(passbg, "passcodeBgImage@2x.png"); save_img(passbg, "passcodeBgImage@3x.png")

def tabbar(size):
    return gradient(size, (255, 220, 234), (255, 205, 224))
save_img(tabbar((750, 106)), "maintabBgImage@2x.png")
save_img(tabbar((1125, 159)), "maintabBgImage@3x.png")


# ===========================================================================
# Tab icons (normal=muted, Selected=accent).  2x:76x58  3x:156x118
# ===========================================================================
print("tab icons...")
def _icon(fn, color, w, h):
    s = 4
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), w * s, h * s, color)
    return im.resize((w, h), Image.LANCZOS)

def gi_friends(d, W, H, c):
    # clean bunny head: round face + two upright ears
    cx, cy, r = W // 2, int(H * 0.62), int(H * 0.25)
    ew = int(W * 0.05)
    for sx in (-1, 1):
        ex = cx + sx * int(W * 0.10)
        d.ellipse([ex - ew, cy - r - int(H * 0.34), ex + ew, cy - r + int(H * 0.06)], fill=c)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

def gi_chats(d, W, H, c):
    cx = W // 2
    for sx in (-1, 1):
        d.ellipse([cx + sx * int(W * 0.15) - int(W * 0.045), int(H * 0.16),
                   cx + sx * int(W * 0.15) + int(W * 0.045), int(H * 0.44)], fill=c)
    d.rounded_rectangle([int(W * 0.24), int(H * 0.40), int(W * 0.76), int(H * 0.80)],
                        radius=int(H * 0.16), fill=c)
    d.polygon([(int(W * 0.32), int(H * 0.78)), (int(W * 0.24), int(H * 0.95)),
               (int(W * 0.46), int(H * 0.78))], fill=c)

def gi_browse(d, W, H, c):
    cx, cy, r = int(W * 0.44), int(H * 0.44), int(H * 0.25)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=int(H * 0.10))
    d.line([cx + int(r * 0.7), cy + int(r * 0.7), int(W * 0.80), int(H * 0.84)],
           fill=c, width=int(H * 0.11))

def gi_game(d, W, H, c):
    for sx in (-1, 1):
        d.ellipse([W // 2 + sx * int(W * 0.20) - int(W * 0.045), int(H * 0.16),
                   W // 2 + sx * int(W * 0.20) + int(W * 0.045), int(H * 0.40)], fill=c)
    d.rounded_rectangle([int(W * 0.20), int(H * 0.36), int(W * 0.80), int(H * 0.78)],
                        radius=int(H * 0.18), fill=c)

def gi_more(d, W, H, c):
    cy, r = H // 2, int(H * 0.09)
    for x in (int(W * 0.30), int(W * 0.50), int(W * 0.70)):
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=c)

# Friends, Chats, Browse(=3rd tab), Find, Piccoma, Game, More
TAB = {
    "maintabIcoFriends": gi_friends, "maintabIcoChats": gi_chats,
    "maintabIcoBrowse": gi_browse,   "maintabIcoFind": gi_browse,
    "maintabIcoPiccoma": gi_more,    "maintabIcoGame": gi_game,
    "maintabIcoMore": gi_more,
}
for name, fn in TAB.items():
    _icon(fn, MUTED, 76, 58).save(os.path.join(IMG, f"{name}@2x.png"))
    _icon(fn, MUTED, 156, 118).save(os.path.join(IMG, f"{name}@3x.png"))
    _icon(fn, ACCENT, 76, 58).save(os.path.join(IMG, f"{name}Selected@2x.png"))
    _icon(fn, ACCENT, 156, 118).save(os.path.join(IMG, f"{name}Selected@3x.png"))


# ===========================================================================
# Theme icon, default profile, add-friend, passcode bullets & keypad
# ===========================================================================
print("icons & passcode...")
def bunny_face(size, with_bg=True):
    """Clean white bunny on a soft pastel circle (used for profile + theme icon)."""
    s = 4
    W = size * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if with_bg:
        d.ellipse([0, 0, W, W], fill=(255, 226, 237))
    cx, cy, r = W // 2, int(W * 0.58), int(W * 0.26)
    line = (242, 212, 224)
    lwf = max(2, int(W * 0.010))
    white = (255, 255, 255)
    ew = int(W * 0.085)
    for sx in (-1, 1):                       # upright ears
        ex = cx + sx * int(W * 0.12)
        d.ellipse([ex - ew, cy - r - int(W * 0.30), ex + ew, cy - r + int(W * 0.05)],
                  fill=white, outline=line, width=lwf)
        d.ellipse([ex - int(ew * 0.5), cy - r - int(W * 0.25),
                   ex + int(ew * 0.5), cy - r - int(W * 0.02)], fill=(255, 205, 219))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=white, outline=line, width=lwf)
    for sx in (-1, 1):                       # two simple eyes
        d.ellipse([cx + sx * int(r * 0.42) - int(r * 0.085), cy - int(r * 0.02),
                   cx + sx * int(r * 0.42) + int(r * 0.085), cy + int(r * 0.20)], fill=TEXT_DARK)
    d.ellipse([cx - int(r * 0.09), cy + int(r * 0.18),                 # tiny nose
               cx + int(r * 0.09), cy + int(r * 0.34)], fill=(255, 150, 180))
    return im.resize((size, size), Image.LANCZOS)

bunny_face(162).save(os.path.join(IMG, "commonIcoTheme.png"))
prof = bunny_face(240)
prof.save(os.path.join(IMG, "profileImg01@2x.png"))
prof.save(os.path.join(IMG, "profileImg01@3x.png"))

def add_friend(w, h):
    s = 4
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gi_friends(d, int(w * s * 0.82), int(h * s), ACCENT)
    cx, cy, r = int(w * s * 0.80), int(h * s * 0.30), int(h * s * 0.16)
    d.line([cx - r, cy, cx + r, cy], fill=ACCENT, width=int(h * s * 0.09))
    d.line([cx, cy - r, cx, cy + r], fill=ACCENT, width=int(h * s * 0.09))
    return im.resize((w, h), Image.LANCZOS)
add_friend(84, 68).save(os.path.join(IMG, "findBtnAddFriend@2x.png"))
add_friend(126, 102).save(os.path.join(IMG, "findBtnAddFriend@3x.png"))

def passcode_dot(px, filled):
    s = 4
    W = px * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = int(W * 0.32)
    if filled:
        d.ellipse([m, m, W - m, W - m], fill=ACCENT)
    else:
        d.ellipse([m, m, W - m, W - m], outline=MUTED, width=int(W * 0.05))
    return im.resize((px, px), Image.LANCZOS)

for i in (1, 2, 3, 4):
    for suf in ("@2x", "@3x"):
        passcode_dot(132, False).save(os.path.join(IMG, f"passcodeImgCode0{i}{suf}.png"))
        passcode_dot(132, True).save(os.path.join(IMG, f"passcodeImgCode0{i}Selected{suf}.png"))

def keypad(px):
    s = 4
    W = px * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([int(W * 0.08)] * 2 + [int(W * 0.92)] * 2,
                               fill=(255, 209, 226, 235))
    return im.resize((px, px), Image.LANCZOS)
keypad(90).save(os.path.join(IMG, "passcodeKeypadPressed.png"))
keypad(120).save(os.path.join(IMG, "passcodeKeypadPressed@2x.png"))
keypad(180).save(os.path.join(IMG, "passcodeKeypadPressed@3x.png"))


# ===========================================================================
# Verification + preview (not shipped in the .ktheme)
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

send3 = _bubble_master(PINK, PINK_EAR, PINK_LINE).resize((BUB_W * 3, BUB_H * 3), Image.LANCZOS)
recv3 = _bubble_master(MINT, MINT_EAR, MINT_LINE).resize((BUB_W * 3, BUB_H * 3), Image.LANCZOS)
cap3 = 20 * 3  # 20px (1x) on the @3x image

# (a) stretch proof
verify = Image.new("RGBA", (760, 280), (250, 244, 250, 255))
for i, (w, h) in enumerate([(BUB_W * 3, BUB_H * 3), (430, BUB_H * 3), (430, 240), (190, 240)]):
    verify.alpha_composite(nine_slice(send3, cap3, w, h), (10 + i * 185, 20))
verify.convert("RGB").save(os.path.join(PREV, "verify_stretch.png"))

# (b) chat mockup
PW, PH = 414, 736
mock = pattern_bg((PW, PH), 40, seed=11).convert("RGBA")
md = ImageDraw.Draw(mock)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
    sf = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except Exception:
    f = sf = ImageFont.load_default()
md.rectangle([0, 0, PW, 54], fill=(255, 215, 232))
_bunny(md, PW // 2 - 64, 30, 6, (255, 120, 165, 255))
md.text((PW // 2 + 6, 27), "Pastel Bunny", font=f, fill=TEXT_DARK, anchor="mm")

def msg(text, side, y):
    tw = int((60 + len(text) * 7) * 1.0)
    src = recv3 if side == "L" else send3
    b = nine_slice(src, cap3, tw, 120)
    b = b.resize((int(b.width * 0.55), int(b.height * 0.55)), Image.LANCZOS)
    x = 14 if side == "L" else PW - 14 - b.width
    mock.alpha_composite(b, (x, y))
    md.text((x + b.width // 2, y + b.height // 2 + 2), text, font=sf, fill=TEXT_DARK, anchor="mm")

msg("hi there!", "L", 86)
msg("hello~ how are you?", "R", 168)
msg("so cute!!", "L", 262)

TBH = 58
mock.alpha_composite(tabbar((PW, TBH)).convert("RGBA"), (0, PH - TBH))
order = [("Friends", gi_friends, True), ("Chats", gi_chats, False),
         ("Find", gi_browse, False), ("Shop", gi_game, False), ("More", gi_more, False)]
slot = PW // len(order)
for i, (lab, fn, on) in enumerate(order):
    col = ACCENT if on else MUTED
    mock.alpha_composite(_icon(fn, col, 30, 24), (i * slot + (slot - 30) // 2, PH - TBH + 8))
    md.text((i * slot + slot // 2, PH - 11), lab, font=sf, fill=col, anchor="mm")

mock.convert("RGB").save(os.path.join(PREV, "preview.png"))
bunny_face(162).save(os.path.join(PREV, "thumbnail.png"))

print("done.")
