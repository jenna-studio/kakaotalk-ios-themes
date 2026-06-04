#!/usr/bin/env python3
"""
Generate PNG assets for the "Pastel Bunny" KakaoTalk iOS theme.

Everything is drawn at @3x and downscaled to @2x / @1x so the Retina
variants stay crisp. The headline assets are the two-eared bunny chat
bubbles: pink for the sender, mint for the receiver.

Run:  python3 scripts/generate_images.py
Output: theme/Images/*.png  and  preview/preview.png
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "theme", "Images")
PREVIEW_DIR = os.path.join(ROOT, "preview")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

# Supersampling factor for smooth anti-aliased edges.
SS = 4

# ---- Pastel palette -------------------------------------------------------
PINK        = (255, 194, 219)   # sender bubble
PINK_EAR_IN = (255, 169, 200)   # sender inner ear
PINK_LINE   = (238, 158, 188)   # sender outline

MINT        = (185, 233, 214)   # receiver bubble
MINT_EAR_IN = (151, 214, 190)   # receiver inner ear
MINT_LINE   = (150, 210, 184)   # receiver outline

BG_TOP      = (255, 244, 250)   # chatroom gradient top (soft pink)
BG_BOT      = (235, 246, 255)   # chatroom gradient bottom (soft sky)
LIST_TOP    = (255, 250, 253)
LIST_BOT    = (245, 250, 255)

TEXT_DARK   = (92, 74, 84)
WHITE       = (255, 255, 255)


# ---- helpers --------------------------------------------------------------
def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def ear(size, color, inner, line):
    """Return an RGBA image of a single short bunny ear (vertical)."""
    w, h = size
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, w - 1, h - 1], fill=color, outline=line, width=max(2, w // 18))
    # inner ear
    iw, ih = int(w * 0.46), int(h * 0.6)
    ix, iy = (w - iw) // 2, int(h * 0.22)
    d.ellipse([ix, iy, ix + iw, iy + ih], fill=inner)
    return im


def bunny_bubble(fill, inner, line, tail="left"):
    """
    Draw a chat bubble shaped like a bunny head: a rounded-rectangle body
    with two short ears on top and a small tail nub on `tail` side.
    Drawn at @3x logical size (supersampled internally).
    Returns an RGBA PIL image.
    """
    # @3x logical canvas
    W, H = 300, 200
    cw, ch = W * SS, H * SS
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lw = 3 * SS  # outline width

    body_top = int(58 * SS)           # leave headroom for ears
    body = [int(10 * SS), body_top, int(290 * SS), int(190 * SS)]
    radius = int(46 * SS)

    # --- ears (drawn first so the body overlaps their base) ---
    ear_w, ear_h = int(56 * SS), int(78 * SS)
    e = ear((ear_w, ear_h), fill, inner, line)
    # left ear, tilted slightly out
    le = e.rotate(16, expand=True, resample=Image.BICUBIC)
    re = e.transpose(Image.FLIP_LEFT_RIGHT).rotate(-16, expand=True, resample=Image.BICUBIC)
    cx = (body[0] + body[2]) // 2
    gap = int(20 * SS)
    im.alpha_composite(le, (cx - le.width - gap // 2 + int(6 * SS), int(6 * SS)))
    im.alpha_composite(re, (cx + gap // 2 - int(6 * SS), int(6 * SS)))

    # --- tail nub ---
    nub = int(26 * SS)
    if tail == "left":
        nx = body[0] - int(8 * SS)
    else:
        nx = body[2] - nub + int(8 * SS)
    ny = body[3] - int(40 * SS)
    d.ellipse([nx, ny, nx + nub, ny + nub], fill=fill, outline=line, width=lw)

    # --- body (covers ear bases & nub seam) ---
    rounded(d, body, radius, fill=fill, outline=line, width=lw)
    # re-fill interior to hide overlapping outlines from ears/nub
    rounded(d, [body[0] + lw, body_top + lw, body[2] - lw, body[3] - lw],
            radius, fill=fill)

    # downscale to @3x
    out = im.resize((W, H), Image.LANCZOS)
    return out


def gradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((w, h))


def _motif_bunny(d, x, y, s, c):
    d.ellipse([x - s, y - s, x + s, y + s], fill=c)                       # face
    for sx in (-1, 1):                                                     # ears
        d.ellipse([x + sx * int(s * 0.5) - int(s * 0.28), y - int(s * 1.9),
                   x + sx * int(s * 0.5) + int(s * 0.28), y - int(s * 0.4)], fill=c)


def _motif_heart(d, x, y, s, c):
    d.ellipse([x - s, y - s, x, y], fill=c)
    d.ellipse([x, y - s, x + s, y], fill=c)
    d.polygon([(x - s, y - int(s * 0.35)), (x + s, y - int(s * 0.35)),
               (x, y + s)], fill=c)


def _motif_carrot(d, x, y, s, c, leaf):
    d.polygon([(x, y + int(s * 1.6)), (x - int(s * 0.6), y - int(s * 0.4)),
               (x + int(s * 0.6), y - int(s * 0.4))], fill=c)             # body
    for off in (-0.4, 0, 0.4):                                            # leaves
        d.ellipse([x + int(off * s) - int(s * 0.18), y - int(s * 1.1),
                   x + int(off * s) + int(s * 0.18), y - int(s * 0.2)], fill=leaf)


def cute_pattern(img, density=70):
    """Scatter faint bunnies, hearts and carrots across the background."""
    import random
    random.seed(11)
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    palette = [(255, 170, 200), (255, 150, 185), (170, 215, 255), (180, 230, 205)]
    for _ in range(density):
        x = random.randint(0, w)
        y = random.randint(0, h)
        s = random.randint(w // 70, w // 40)
        a = random.randint(26, 52)
        base = random.choice(palette)
        c = base + (a,)
        kind = random.random()
        if kind < 0.45:
            _motif_bunny(d, x, y, s, c)
        elif kind < 0.8:
            _motif_heart(d, x, y, int(s * 1.1), c)
        else:
            _motif_carrot(d, x, y, s, (255, 165, 110, a), (170, 220, 160, a))
    img = img.convert("RGBA")
    return Image.alpha_composite(img, layer).convert("RGB")


# ---- tab bar icons --------------------------------------------------------
TAB_OFF = (185, 141, 160)   # normal (muted mauve)
TAB_ON  = (255, 111, 163)   # selected (pink)


def _icon_base():
    S = 75 * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), S


def _ear_pair(d, S, color, cx, base_y, ew, eh, spread):
    """Two short upright ears centered on cx with their base at base_y."""
    for sign in (-1, 1):
        ex = cx + sign * spread - ew // 2
        d.ellipse([ex, base_y - eh, ex + ew, base_y + eh // 4], fill=color)


def icon_friends(color):
    """Bunny head: round face with two short ears."""
    im, d, S = _icon_base()
    cx = S // 2
    fr = int(S * 0.27)            # face radius
    fcy = int(S * 0.60)
    _ear_pair(d, S, color, cx, fcy - fr + int(S * 0.04),
              ew=int(S * 0.16), eh=int(S * 0.24), spread=int(S * 0.13))
    d.ellipse([cx - fr, fcy - fr, cx + fr, fcy + fr], fill=color)
    return im.resize((75, 75), Image.LANCZOS)


def icon_chats(color):
    """Speech bubble with two short ears and a tail nub."""
    im, d, S = _icon_base()
    cx = S // 2
    bx0, by0, bx1, by1 = int(S * 0.20), int(S * 0.42), int(S * 0.80), int(S * 0.78)
    _ear_pair(d, S, color, cx, by0 + int(S * 0.04),
              ew=int(S * 0.15), eh=int(S * 0.22), spread=int(S * 0.16))
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=int(S * 0.16), fill=color)
    d.polygon([(bx0 + int(S * 0.10), by1 - int(S * 0.02)),
               (bx0 + int(S * 0.02), by1 + int(S * 0.12)),
               (bx0 + int(S * 0.24), by1 - int(S * 0.02))], fill=color)
    return im.resize((75, 75), Image.LANCZOS)


def icon_openchat(color):
    """Two overlapping bubbles, the back one wearing ears."""
    im, d, S = _icon_base()
    # back bubble (with ears)
    _ear_pair(d, S, color, int(S * 0.42), int(S * 0.36),
              ew=int(S * 0.13), eh=int(S * 0.19), spread=int(S * 0.13))
    d.rounded_rectangle([int(S * 0.16), int(S * 0.34), int(S * 0.66), int(S * 0.66)],
                        radius=int(S * 0.14), fill=color)
    # front bubble (clear notch so it reads as two)
    d.rounded_rectangle([int(S * 0.40), int(S * 0.50), int(S * 0.86), int(S * 0.80)],
                        radius=int(S * 0.14), outline=color, width=int(S * 0.06))
    im2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(im2)
    d2.rounded_rectangle([int(S * 0.40), int(S * 0.50), int(S * 0.86), int(S * 0.80)],
                         radius=int(S * 0.14), fill=color)
    # punch a gap between the two so they don't merge into a blob
    gap = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dg = ImageDraw.Draw(gap)
    dg.rounded_rectangle([int(S * 0.36), int(S * 0.46), int(S * 0.46), int(S * 0.84)],
                         radius=int(S * 0.05), fill=(0, 0, 0, 255))
    base = Image.alpha_composite(im, im2)
    base_px = base.load()
    gap_px = gap.load()
    for y in range(S):
        for x in range(S):
            if gap_px[x, y][3] > 0:
                base_px[x, y] = (0, 0, 0, 0)
    return base.resize((75, 75), Image.LANCZOS)


def icon_more(color):
    """Three dots with a tiny pair of ears on the middle one."""
    im, d, S = _icon_base()
    r = int(S * 0.09)
    cy = S // 2
    xs = [int(S * 0.30), int(S * 0.50), int(S * 0.70)]
    _ear_pair(d, S, color, xs[1], cy - r - int(S * 0.02),
              ew=int(S * 0.09), eh=int(S * 0.13), spread=int(S * 0.06))
    for x in xs:
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=color)
    return im.resize((75, 75), Image.LANCZOS)


TAB_ICONS = {
    "tab_friends":  icon_friends,
    "tab_chats":    icon_chats,
    "tab_openchat": icon_openchat,
    "tab_more":     icon_more,
}


def save_variants(img3x, name):
    """img3x is the @3x master. Save @1x/@2x/@3x PNGs."""
    w3, h3 = img3x.size
    variants = {
        "":    (w3 // 3, h3 // 3),
        "@2x": (w3 * 2 // 3, h3 * 2 // 3),
        "@3x": (w3, h3),
    }
    for suffix, size in variants.items():
        out = img3x.resize(size, Image.LANCZOS) if size != (w3, h3) else img3x
        out.save(os.path.join(IMG_DIR, f"{name}{suffix}.png"))


# ---- generate bubbles (master is @3x already) -----------------------------
def bubble_master(fill, inner, line, tail):
    # bunny_bubble returns @3x sized (300x200). Treat as @3x master.
    return bunny_bubble(fill, inner, line, tail)


print("Generating bunny chat bubbles...")
sent = bubble_master(PINK, PINK_EAR_IN, PINK_LINE, tail="right")
recv = bubble_master(MINT, MINT_EAR_IN, MINT_LINE, tail="left")
save_variants(sent, "chatBubbleSent")
save_variants(recv, "chatBubbleReceived")

# ---- backgrounds ----------------------------------------------------------
print("Generating backgrounds...")
# Chatroom background @3x ~ 1242 x 2688 is huge; keep a tileable medium size.
chat_bg = gradient((1242, 2208), BG_TOP, BG_BOT)
chat_bg = cute_pattern(chat_bg, density=120)
chat_bg.save(os.path.join(IMG_DIR, "bg_chatroom@3x.png"))
chat_bg.resize((828, 1472), Image.LANCZOS).save(os.path.join(IMG_DIR, "bg_chatroom@2x.png"))
chat_bg.resize((414, 736), Image.LANCZOS).save(os.path.join(IMG_DIR, "bg_chatroom.png"))

# Friends / chats lists get a lighter version of the same motif so the whole
# theme feels like one set.
for nm in ("bg_friends", "bg_chats"):
    g = gradient((1242, 2208), LIST_TOP, LIST_BOT)
    g = cute_pattern(g, density=55)
    g.save(os.path.join(IMG_DIR, f"{nm}@3x.png"))
    g.resize((828, 1472), Image.LANCZOS).save(os.path.join(IMG_DIR, f"{nm}@2x.png"))
    g.resize((414, 736), Image.LANCZOS).save(os.path.join(IMG_DIR, f"{nm}.png"))

# ---- tab bar icons --------------------------------------------------------
print("Generating tab bar icons...")
for nm, fn in TAB_ICONS.items():
    save_variants(fn(TAB_OFF), nm)          # normal state
    save_variants(fn(TAB_ON), nm + "_on")   # selected state

# ---- preview mockup -------------------------------------------------------
print("Rendering preview mockup...")
PW, PH = 414, 736
mock = gradient((PW, PH), BG_TOP, BG_BOT)
mock = cute_pattern(mock, density=42).convert("RGBA")
md = ImageDraw.Draw(mock)

# nav bar
md.rectangle([0, 0, PW, 64], fill=(255, 209, 226))
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    sfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except Exception:
    font = ImageFont.load_default()
    sfont = ImageFont.load_default()
_motif_bunny(md, PW // 2 - 92, 34, 7, (255, 120, 165, 255))
md.text((PW // 2 + 6, 36), "Pastel Bunny", font=font, fill=TEXT_DARK, anchor="mm")

def place_bubble(master, x, y, scale):
    b = master.resize((int(master.width * scale), int(master.height * scale)), Image.LANCZOS)
    mock.alpha_composite(b, (x, y))
    return b

# received (mint) on left, sent (pink) on right
b1 = place_bubble(recv, 16, 110, 0.42)
md.text((16 + b1.width // 2, 110 + b1.height // 2 + 6),
        "hi there!", font=sfont, fill=TEXT_DARK, anchor="mm")
b2 = place_bubble(sent, PW - 16 - int(sent.width * 0.42), 210, 0.42)
md.text((PW - 16 - int(sent.width * 0.42) // 2 - 6, 210 + b2.height // 2 + 6),
        "hello~", font=sfont, fill=TEXT_DARK, anchor="mm")
b3 = place_bubble(recv, 16, 320, 0.42)
md.text((16 + b3.width // 2, 320 + b3.height // 2 + 6),
        "so cute!", font=sfont, fill=TEXT_DARK, anchor="mm")

# bottom tab bar with the bunny icons
TB_H = 64
md.rectangle([0, PH - TB_H, PW, PH], fill=(255, 209, 226))
tab_order = [("tab_friends", True), ("tab_chats", False),
             ("tab_openchat", False), ("tab_more", False)]
slot = PW // len(tab_order)
labels = ["Friends", "Chats", "Open", "More"]
for i, (nm, on) in enumerate(tab_order):
    col = TAB_ON if on else TAB_OFF
    icon = (icon_friends if nm == "tab_friends" else
            icon_chats if nm == "tab_chats" else
            icon_openchat if nm == "tab_openchat" else icon_more)(col)
    icon = icon.resize((30, 30), Image.LANCZOS)
    ix = i * slot + (slot - 30) // 2
    mock.alpha_composite(icon, (ix, PH - TB_H + 8))
    md.text((i * slot + slot // 2, PH - 14), labels[i], font=sfont,
            fill=col, anchor="mm")

mock.convert("RGB").save(os.path.join(PREVIEW_DIR, "preview.png"))

# ---- theme thumbnail (tile shown in KakaoTalk's theme list) ---------------
print("Rendering theme thumbnail...")
# Master at @3x; portrait tile like a mini phone screen.
TW, TH = 540, 720
thumb = gradient((TW, TH), BG_TOP, BG_BOT)
thumb = cute_pattern(thumb, density=60).convert("RGBA")
td = ImageDraw.Draw(thumb)

try:
    big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    tin = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
except Exception:
    big = sub = tin = ImageFont.load_default()

# soft rounded inner frame
td.rounded_rectangle([18, 18, TW - 18, TH - 18], radius=42,
                     outline=(255, 255, 255, 180), width=8)

# hero: a big pink bunny bubble + a smaller mint one, overlapping
hero = sent.resize((int(sent.width * 1.15), int(sent.height * 1.15)), Image.LANCZOS)
thumb.alpha_composite(hero, ((TW - hero.width) // 2 + 28, 250))
mini = recv.resize((int(recv.width * 0.72), int(recv.height * 0.72)), Image.LANCZOS)
thumb.alpha_composite(mini, (54, 360))

# decorative bunnies in the corners
_motif_bunny(td, 70, 70, 16, (255, 130, 170, 200))
_motif_bunny(td, TW - 80, 96, 13, (160, 210, 255, 200))

# title
td.text((TW // 2, 150), "Pastel", font=big, fill=(255, 111, 163), anchor="mm")
td.text((TW // 2, 210), "Bunny", font=big, fill=TEXT_DARK, anchor="mm")
td.text((TW // 2, TH - 70), "KakaoTalk theme", font=tin, fill=(150, 120, 134),
        anchor="mm")

thumb_rgb = thumb.convert("RGB")
save_variants(thumb_rgb, "thumbnail")          # theme/Images/thumbnail*.png
thumb_rgb.save(os.path.join(PREVIEW_DIR, "thumbnail.png"))

print("Done. Assets in theme/Images/, previews in preview/")
