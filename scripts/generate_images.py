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


def scatter_pattern(img, color, density=26):
    """Sprinkle faint hearts / dots over a background for cuteness."""
    import random
    random.seed(7)
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(density):
        x = random.randint(0, w)
        y = random.randint(0, h)
        s = random.randint(w // 60, w // 32)
        a = random.randint(22, 46)
        c = color + (a,)
        # tiny dot
        d.ellipse([x, y, x + s, y + s], fill=c)
    img = img.convert("RGBA")
    return Image.alpha_composite(img, layer).convert("RGB")


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
chat_bg = scatter_pattern(chat_bg, (255, 180, 205), density=40)
chat_bg.save(os.path.join(IMG_DIR, "bg_chatroom@3x.png"))
chat_bg.resize((828, 1472), Image.LANCZOS).save(os.path.join(IMG_DIR, "bg_chatroom@2x.png"))
chat_bg.resize((414, 736), Image.LANCZOS).save(os.path.join(IMG_DIR, "bg_chatroom.png"))

for nm in ("bg_friends", "bg_chats"):
    g = gradient((1242, 2208), LIST_TOP, LIST_BOT)
    g.save(os.path.join(IMG_DIR, f"{nm}@3x.png"))
    g.resize((828, 1472), Image.LANCZOS).save(os.path.join(IMG_DIR, f"{nm}@2x.png"))
    g.resize((414, 736), Image.LANCZOS).save(os.path.join(IMG_DIR, f"{nm}.png"))

# ---- preview mockup -------------------------------------------------------
print("Rendering preview mockup...")
PW, PH = 414, 736
mock = gradient((PW, PH), BG_TOP, BG_BOT)
mock = scatter_pattern(mock, (255, 180, 205), density=18).convert("RGBA")
md = ImageDraw.Draw(mock)

# nav bar
md.rectangle([0, 0, PW, 64], fill=(255, 209, 226))
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    sfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
except Exception:
    font = ImageFont.load_default()
    sfont = ImageFont.load_default()
md.text((PW // 2, 36), "🐰 Bunny Chat", font=font, fill=TEXT_DARK, anchor="mm")

def place_bubble(master, x, y, scale):
    b = master.resize((int(master.width * scale), int(master.height * scale)), Image.LANCZOS)
    mock.alpha_composite(b, (x, y))
    return b

# received (mint) on left, sent (pink) on right
b1 = place_bubble(recv, 16, 110, 0.42)
md.text((16 + b1.width // 2, 110 + b1.height // 2 + 6),
        "hi! 🐇", font=sfont, fill=TEXT_DARK, anchor="mm")
b2 = place_bubble(sent, PW - 16 - int(sent.width * 0.42), 210, 0.42)
md.text((PW - 16 - int(sent.width * 0.42) // 2 - 6, 210 + b2.height // 2 + 6),
        "hello~", font=sfont, fill=TEXT_DARK, anchor="mm")
b3 = place_bubble(recv, 16, 320, 0.42)
md.text((16 + b3.width // 2, 320 + b3.height // 2 + 6),
        "so cute!", font=sfont, fill=TEXT_DARK, anchor="mm")

mock.convert("RGB").save(os.path.join(PREVIEW_DIR, "preview.png"))

print("Done. Assets in theme/Images/, preview in preview/preview.png")
