#!/usr/bin/env python3
"""
Generate every PNG asset for the "Pixel Daydream" KakaoTalk iOS theme.

Look (matching the reference mockups):
  * Backgrounds: pink -> lavender -> baby-blue vertical gradient, with a
    checkered pixel border along the top and bottom edges and a faint scatter
    of pixel butterflies / hearts / sparkles.
  * Chat bubbles: retro "chat window" frames. Received = pink window with a
    pink title bar; sent = periwinkle window with a blue title bar. Each title
    bar carries a tiny butterfly (top-left) and minimize/close buttons
    (top-right), placed inside the 9-slice corner cap so they never distort.
  * Tab icons, passcode bullets, default profiles and the theme icon are drawn
    as crisp, integer-scaled PIXEL art.

Conventions from the official KakaoTalk 8.0.0 iOS Theme User Guide:
  * Images are 2x-based:  name.png == name@2x.png (2x px),  name@3x.png (3x px)
  * Insets/caps in the CSS are 1x-based
  * Bubbles are 9-slice stretched with a `22px 22px` cap (1x).

Run: python3 scripts/generate_images.py
"""

import os
import random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "Images")
PREV = os.path.join(ROOT, "preview")
os.makedirs(IMG, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

# ---- dreamy pastel palette ------------------------------------------------
BG_TOP   = (249, 214, 234)   # pink
BG_MID   = (215, 198, 242)   # lavender
BG_BOT   = (194, 224, 247)   # baby blue
PASS_TOP = (245, 220, 240)
PASS_BOT = (210, 226, 248)

CHK_PINK  = (244, 184, 216)
CHK_BLUE  = (174, 219, 242)
CHK_WHITE = (255, 250, 253)

# retro chat-window bubbles
SENT_BORDER = (140, 180, 230)
SENT_TITLE  = (182, 212, 242)
SENT_BODY   = (220, 234, 250, 236)
SENT_DIV    = (150, 188, 232)

RECV_BORDER = (238, 164, 200)
RECV_TITLE  = (248, 200, 221)
RECV_BODY   = (255, 244, 250, 240)
RECV_DIV    = (240, 172, 202)

TEXT_DARK = (106, 90, 122)
MUTED     = (179, 160, 204)
ACCENT    = (240, 106, 160)

# pixel heart colours (passcode bullets, profiles, scatter)
H_PURPLE = (183, 156, 234)
H_PINK   = (244, 166, 206)
H_BLUE   = (156, 200, 242)
H_GREEN  = (166, 226, 182)
H_YELLOW = (245, 224, 150)

BFLY_CYAN = (143, 224, 224)
BFLY_PINK = (246, 168, 208)
STAR      = (247, 230, 150)


def darken(c, f=0.88):
    return tuple(max(0, int(v * f)) for v in c[:3]) + (tuple(c[3:]) if len(c) > 3 else ())


def save(img, name):
    img.save(os.path.join(IMG, name))


# ===========================================================================
# Pixel-art helpers
# ===========================================================================
# Sprites are written as a list of equal-ish rows of single-char codes mapped
# to colours via a palette dict. '.' / ' ' = transparent. We rasterise on an
# integer grid so the pixels stay crisp at any output size (NEAREST-style).

def _dims(rows):
    return max(len(r) for r in rows), len(rows)


def draw_pixels(d, rows, palette, ox, oy, cell):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = palette.get(ch)
            if col:
                d.rectangle([ox + x * cell, oy + y * cell,
                             ox + x * cell + cell - 1, oy + y * cell + cell - 1],
                            fill=col)


def sprite_canvas(rows, palette, cw, ch, ratio=0.82, cell=None):
    """Render a sprite centred on a cw x ch transparent canvas, crisp pixels."""
    sw, sh = _dims(rows)
    if cell is None:
        cell = max(1, int(min(cw * ratio / sw, ch * ratio / sh)))
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ox = (cw - sw * cell) // 2
    oy = (ch - sh * cell) // 2
    draw_pixels(ImageDraw.Draw(im), rows, palette, ox, oy, cell)
    return im


# ---- sprite shapes --------------------------------------------------------
BUTTERFLY = [
    "..o.....o..",
    ".oWo...oWo.",
    "oWWWo.oWWWo",
    "oWWWWoWWWWo",
    ".oWWWbWWWo.",
    ".oWWWbWWWo.",
    "oWWWWoWWWWo",
    "oWWWo.oWWWo",
    ".oWo...oWo.",
]

HEART = [
    ".oo.oo.",
    "oXXoXXo",
    "oXXXXXo",
    "oXXXXXo",
    ".oXXXo.",
    "..oXo..",
    "...o...",
]

HEART_OUTLINE = [
    ".oo.oo.",
    "o..o..o",
    "o.....o",
    "o.....o",
    ".o...o.",
    "..o.o..",
    "...o...",
]

SPARKLE = [
    "...o...",
    "...Y...",
    "..YYY..",
    "oYYSYYo",
    "..YYY..",
    "...Y...",
    "...o...",
]

CLOUD = [
    "...ooo....",
    "..oWWWoo..",
    ".oWWWWWWo.",
    "oWWWWWWWWo",
    "oWWWWWWWWo",
    ".oooooooo.",
]

STAR5 = [
    "....o....",
    "....Y....",
    "...YYY...",
    "oooYYYooo",
    ".oYYYYYo.",
    "..YYYYY..",
    ".oYY.YYo.",
    ".o.....o.",
]

PERSON = [
    "...ooo...",
    "..oWWWo..",
    "..oWWWo..",
    "...ooo...",
    ".........",
    ".ooooooo.",
    "oWWWWWWWo",
    "oWWWWWWWo",
    "oWWWWWWWo",
    "oWWWWWWWo",
]

PHONE = [
    ".ooooo.",
    "oWWWWWo",
    "oWbbbWo",
    "oWbbbWo",
    "oWbbbWo",
    "oWbbbWo",
    "oWWWWWo",
    "oWWoWWo",
    ".ooooo.",
]

GRID = [
    "oo.oo",
    "oo.oo",
    ".....",
    "oo.oo",
    "oo.oo",
]


def pal_butterfly(wing, edge, body=(120, 104, 140)):
    return {"o": edge, "W": wing, "b": body}


def pal_heart(fill, edge=None):
    edge = edge or darken(fill, 0.78)
    return {"o": edge, "X": fill}


def pal_heart_outline(edge):
    return {"o": edge}


def pal_sparkle(c=STAR):
    e = darken(c, 0.8)
    hi = tuple(min(255, int(v * 1.12)) for v in c)
    return {"o": e, "Y": c, "S": hi}


def pal_cloud(w=(255, 252, 255), e=(190, 206, 232)):
    return {"o": e, "W": w}


def pal_star(c=STAR):
    return {"o": darken(c, 0.8), "Y": c}


def pal_mono(c):
    e = darken(c, 0.8)
    return {"o": e, "W": c, "b": darken(c, 0.7)}


# ===========================================================================
# Retro "chat window" bubbles
#   A pastel window frame (gradient title bar + butterfly + minimize/close)
#   wrapping an inset, frosted content panel where the text sits. Everything
#   decorative lives inside the 22px 9-slice corner cap, so it never distorts.
# ===========================================================================
DS = 12                       # draw units per 1x point (downscaled -> crisp)
BUB_W, BUB_H = 100, 80        # 1x points
CAP = 24                      # 9-slice cap (matches the CSS). Small enough that
                              # even a 1-line bubble stays taller than 2*CAP, so
                              # the cap never clamps and the TITLE BAR is exactly
                              # the same size on every bubble regardless of text.


def _grad_v(w, h, top, bot):
    col = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        col.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return col.resize((w, h))


def _grad_v_stops(w, h, stops):
    """Vertical multi-stop gradient. Used for the iridescent panel because a
    VERTICAL gradient survives KakaoTalk's 9-slice stretch (every column is
    identical, so horizontal stretching keeps it; a horizontal gradient would
    collapse to a flat colour in the stretched centre)."""
    n = len(stops) - 1
    col = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        seg = min(n - 1, int(t * n))
        k = t * n - seg
        c0, c1 = stops[seg], stops[seg + 1]
        col.putpixel((0, y), tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
    return col.resize((w, h))


def _rounded_mask(w, h, box, r, val=255):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle(box, radius=r, fill=val)
    return m


def _radial_fill(w, h, stops):
    """Circular gradient: stops[0] at the centre -> stops[-1] at the edge.
    Built from PIL's radial gradient (0 centre .. 255 edge) via per-channel
    LUTs, so it's cheap. The edge colour is set to the window frame colour, so
    the panel melts seamlessly into the frame; on stretched bubbles the circle
    becomes a soft ellipse but never a hard band."""
    rad = Image.radial_gradient("L").resize((max(1, w), max(1, h)))
    n = len(stops) - 1

    def lut(ch):
        out = []
        for i in range(256):
            t = i / 255
            seg = min(n - 1, int(t * n))
            k = t * n - seg
            out.append(int(stops[seg][ch] + (stops[seg + 1][ch] - stops[seg][ch]) * k))
        return out

    return Image.merge("RGB", (rad.point(lut(0)), rad.point(lut(1)), rad.point(lut(2))))


# colours per bubble side: frame, title gradient, iridescent panel stops, glow
class Bub:
    def __init__(self, border, frame, title_top, title_bot, panel_stops, div, glow, wing):
        self.border = border
        self.frame = frame
        self.title_top, self.title_bot = title_top, title_bot
        self.panel_stops = panel_stops
        self.div = div
        self.glow = glow
        self.wing = wing

    def dim(self, f):
        d = lambda c: darken(c, f)
        return Bub(d(self.border), d(self.frame), d(self.title_top), d(self.title_bot),
                   [d(c) for c in self.panel_stops], d(self.div), self.glow, d(self.wing))


# panel_stops are now a RADIAL ramp: centre -> edge. The edge equals the window
# frame colour so the panel blends seamlessly into the frame.
# received = pink window: soft-pink centre -> pink -> deeper pink -> pink frame
# (pink-dominant, with just a whisper of mint near the centre)
RECV = Bub(border=(232, 146, 192), frame=(247, 199, 223),
           title_top=(250, 202, 225), title_bot=(238, 197, 227),
           panel_stops=[(255, 247, 251), (250, 226, 240), (249, 208, 228), (247, 199, 223)],
           div=(236, 158, 200), glow=(252, 206, 232, 150), wing=(132, 222, 214))

# sent = periwinkle window: richer hologram -- white centre -> mint -> lavender
# -> periwinkle -> blue frame edge (more colour, still soft and frame-seamless)
SENT = Bub(border=(148, 166, 224), frame=(199, 213, 240),
           title_top=(201, 219, 245), title_bot=(204, 224, 234),
           panel_stops=[(240, 244, 250), (205, 238, 230), (214, 210, 246),
                        (203, 216, 244), (199, 213, 240)],
           div=(158, 178, 226), glow=(200, 216, 246, 150), wing=(140, 224, 204))

PANEL_ALPHA = 242             # frosted: lets a touch of background through


def _bubble_master(b):
    """Render the embossed, glossy hologram window at DS resolution."""
    W, H = BUB_W * DS, BUB_H * DS
    lw = max(2, int(1.6 * DS))
    r_out = 14 * DS
    title_h = 16 * DS
    margin = 6 * DS                  # frame thickness around the inset panel
    r_in = 6 * DS
    panel_gap = 1 * DS               # gap between title bar and the panel
    # NB: title_h + panel_gap + r_in (+border) must stay <= CAP so BOTH the
    # top AND bottom panel corners sit fully inside the 9-slice cap -- otherwise
    # tall bubbles stretch the top corners only and the box flares wider at the
    # bottom.
    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full = [lw // 2, lw // 2, W - lw // 2, H - lw // 2]

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # soft outer glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(full, radius=r_out, fill=b.glow)
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(DS * 1.4)))

    # window frame (solid frame colour inside the rounded rect)
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frame.paste(Image.new("RGBA", (W, H), b.frame + (255,)), (0, 0),
                _rounded_mask(W, H, full, r_out))
    out.alpha_composite(frame)

    # title bar gradient (clipped to the rounded top of the frame)
    tmask = _rounded_mask(W, H, [lw // 2, lw // 2, W - lw // 2, lw // 2 + title_h + r_out], r_out)
    ImageDraw.Draw(tmask).rectangle([0, lw // 2 + title_h, W, H], fill=0)
    tgrad = Image.new("RGB", (W, H), b.title_bot)
    tgrad.paste(_grad_v(W, lw // 2 + title_h, b.title_top, b.title_bot), (0, 0))
    out.paste(tgrad, (0, 0), tmask)

    # ---- inset hologram content panel ------------------------------------
    px0, py0 = margin + lw // 2, lw // 2 + title_h + panel_gap
    px1, py1 = W - margin - lw // 2, H - margin - lw // 2
    pbox = [px0, py0, px1, py1]
    pmask = _rounded_mask(W, H, pbox, r_in, val=PANEL_ALPHA)
    pmask_full = _rounded_mask(W, H, pbox, r_in, val=255)

    # drop shadow beneath the panel -> raised / embossed feel
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [px0, py0 + int(DS * 0.9), px1, py1 + int(DS * 0.9)], radius=r_in, fill=(72, 60, 104, 85))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(DS * 0.8)))

    # circular (radial) fill: bright centre fading to the frame colour at the
    # edges, so the panel blends seamlessly into the window frame.
    pfill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pfill.paste(_radial_fill(px1 - px0, py1 - py0, b.panel_stops).convert("RGBA"), (px0, py0))
    out.paste(pfill, (0, 0), pmask)

    # soft glossy sheen across the top of the panel (subtle, vertical fade)
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    ph = py1 - py0
    for yy in range(py0, py0 + int(ph * 0.48)):
        t = (yy - py0) / max(1, ph * 0.48)
        gd.line([px0, yy, px1, yy], fill=(255, 255, 255, int(62 * (1 - t) ** 1.5)))
    out.alpha_composite(Image.composite(gloss, blank, pmask_full))

    d = ImageDraw.Draw(out)
    # embossed feel via 9-slice-safe horizontal bands: bright top edge,
    # soft shadow bottom edge (inset by the corner radius so they stay inside
    # the rounded panel and never distort when the bubble stretches).
    hi_y = py0 + max(1, int(DS * 0.55))
    lo_y = py1 - max(1, int(DS * 0.55))
    d.line([px0 + r_in, hi_y, px1 - r_in, hi_y], fill=(255, 255, 255, 165),
           width=max(1, int(DS * 0.22)))
    d.line([px0 + r_in, lo_y, px1 - r_in, lo_y], fill=(92, 74, 122, 60),
           width=max(1, int(DS * 0.18)))

    # title divider + chrome top-highlight (glossy window edge)
    d.line([px0, lw // 2 + title_h, px1, lw // 2 + title_h], fill=b.div,
           width=max(1, int(DS * 0.3)))
    d.line([lw // 2 + r_out, lw // 2 + max(1, int(DS * 0.35)),
            W - lw // 2 - r_out, lw // 2 + max(1, int(DS * 0.35))],
           fill=(255, 255, 255, 130), width=max(1, int(DS * 0.22)))

    # outer border
    d.rounded_rectangle(full, radius=r_out, outline=b.border, width=lw)
    return out


def _overlay_widgets(img, scale, b):
    """Crisp pixel butterfly + minimize/close buttons, inset from the edges so
    they sit safely inside the 24px corner cap and never get cropped."""
    d = ImageDraw.Draw(img)
    # pixel butterfly, inset from the LEFT, vertically centred in the title bar
    draw_pixels(d, BUTTERFLY, pal_butterfly(b.wing, darken(b.wing, 0.62)),
                11 * scale, 5 * scale, scale)
    # minimize + close buttons, inset from the RIGHT, centred in the title bar
    edge = darken(b.border, 0.88)
    bfill = (255, 253, 255, 240)
    size = 7
    for i, kind in enumerate(("min", "close")):
        x = (77 + i * 9) * scale
        y = 6 * scale
        x1, y1 = x + size * scale, y + size * scale
        d.rectangle([x, y, x1, y1], fill=bfill, outline=edge, width=max(1, scale // 2))
        if kind == "min":
            d.line([x + 2 * scale, y1 - 1.6 * scale, x1 - 2 * scale, y1 - 1.6 * scale],
                   fill=edge, width=max(1, scale // 2))
        else:
            d.line([x + 2 * scale, y + 2 * scale, x1 - 2 * scale, y1 - 2 * scale],
                   fill=edge, width=max(1, scale // 2))
            d.line([x1 - 2 * scale, y + 2 * scale, x + 2 * scale, y1 - 2 * scale],
                   fill=edge, width=max(1, scale // 2))
    return img


def _bubble_variant(b, scale):
    master = _bubble_master(b)
    img = master.resize((BUB_W * scale, BUB_H * scale), Image.LANCZOS)
    return _overlay_widgets(img, scale, b)


def write_bubble(prefix, b):
    n2, n3 = _bubble_variant(b, 2), _bubble_variant(b, 3)
    s2, s3 = _bubble_variant(b.dim(0.9), 2), _bubble_variant(b.dim(0.9), 3)
    for v in ("01", "02"):
        save(n2, f"{prefix}{v}.png")
        save(n2, f"{prefix}{v}@2x.png")
        save(n3, f"{prefix}{v}@3x.png")
        save(s2, f"{prefix}{v}Selected.png")
        save(s2, f"{prefix}{v}Selected@2x.png")
        save(s3, f"{prefix}{v}Selected@3x.png")


print("bubbles...")
write_bubble("chatroomBubbleReceive", RECV)
write_bubble("chatroomBubbleSend", SENT)


# ===========================================================================
# Backgrounds: gradient + checkered pixel borders + faint pixel scatter
# ===========================================================================
def vgradient(size, stops):
    """Vertical multi-stop gradient. stops = [(pos0..1, color), ...]."""
    w, h = size
    col = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                col.putpixel((0, y), tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3)))
                break
        else:
            col.putpixel((0, y), stops[-1][1])
    return col.resize((w, h))


def checker_band(d, w, y0, rows, cell, colors, seed):
    rnd = random.Random(seed)
    nx = w // cell + 1
    for ry in range(rows):
        for cx in range(nx):
            base = (cx + ry) % 2
            if base == 0:
                c = colors[0]
            else:
                c = colors[1] if rnd.random() < 0.7 else colors[2]
            x = cx * cell
            yy = y0 + ry * cell
            d.rectangle([x, yy, x + cell - 1, yy + cell - 1], fill=c)


def dreamy(size, blobs, base):
    """Soft, cloudy multi-colour pastel wash (overlapping blurred blobs)."""
    w, h = size
    img = Image.new("RGBA", (w, h), base + (255,))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx, cy, rad, col, a in blobs:
        d.ellipse([(cx - rad) * w, (cy - rad) * h, (cx + rad) * w, (cy + rad) * h],
                  fill=col + (a,))
    img = Image.alpha_composite(img, layer)
    return img.convert("RGB").filter(ImageFilter.GaussianBlur(max(w, h) // 6))


# sparse, crisp pixel motifs (matching the reference: few, small, visible)
SCATTER_MOTIFS = [
    (BUTTERFLY, pal_butterfly(BFLY_PINK, darken(BFLY_PINK, 0.65))),
    (BUTTERFLY, pal_butterfly(BFLY_CYAN, darken(BFLY_CYAN, 0.65))),
    (BUTTERFLY, pal_butterfly((158, 226, 188), (108, 188, 148))),
    (HEART, pal_heart(H_PURPLE)),
    (HEART, pal_heart(H_PINK)),
    (SPARKLE, pal_sparkle()),
    (SPARKLE, pal_sparkle()),
]


def scatter(img, cols, rows, seed):
    """Place tiny pixel motifs on a jittered grid so they're spread evenly
    (not clustered) and kept small -- they're just little decorations."""
    rnd = random.Random(seed)
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base = max(2, w // 430)          # ~2px cells -> tiny sprites
    y0, y1 = h * 0.07, h * 0.92
    cw, ch = w / cols, (y1 - y0) / rows
    k = rnd.randrange(len(SCATTER_MOTIFS))
    for r in range(rows):
        for c in range(cols):
            shape, pal = SCATTER_MOTIFS[k % len(SCATTER_MOTIFS)]
            k += 1
            a = rnd.randint(165, 225)
            fpal = {kk: (vv[:3] + (a,)) for kk, vv in pal.items()}
            cell = rnd.choice([base, base, base + 1])
            sw, sh = _dims(shape)
            spr = Image.new("RGBA", (sw * cell, sh * cell), (0, 0, 0, 0))
            draw_pixels(ImageDraw.Draw(spr), shape, fpal, 0, 0, cell)
            cx = c * cw + cw * rnd.uniform(0.22, 0.78)
            cy = y0 + r * ch + ch * rnd.uniform(0.22, 0.78)
            layer.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def make_bg(size, blobs, base, cols, rows, seed, border_cell=None, checker=False):
    w, h = size
    img = dreamy(size, blobs, base).convert("RGBA")
    img = scatter(img, cols, rows, seed)
    if checker:                       # only the chatroom keeps the checker edge
        d = ImageDraw.Draw(img)
        cell = border_cell or max(6, w // 18)
        chk = [CHK_PINK, CHK_BLUE, CHK_WHITE]
        checker_band(d, w, 0, 2, cell, chk, seed + 1)
        checker_band(d, w, h - 2 * cell, 2, cell, chk, seed + 2)
    return img.convert("RGB")


print("backgrounds...")
# cloudy wash: pink top, blue upper-left, lavender right, pink-lilac bottom
MAIN_BLOBS = [
    (0.50, 0.02, 0.70, (250, 208, 233), 255),
    (0.24, 0.40, 0.52, (190, 222, 247), 235),
    (0.18, 0.72, 0.46, (198, 232, 245), 215),
    (0.86, 0.50, 0.56, (214, 200, 242), 225),
    (0.55, 1.00, 0.62, (242, 206, 236), 240),
    (0.62, 0.27, 0.34, (208, 196, 240), 175),
]
MAIN_BASE = (216, 206, 240)
chat = make_bg((846, 1503), MAIN_BLOBS, MAIN_BASE, 4, 7, seed=11, checker=True)
save(chat, "chatroomBgImage@2x.png"); save(chat, "chatroomBgImage@3x.png")
main = make_bg((846, 1503), MAIN_BLOBS, MAIN_BASE, 4, 7, seed=5, checker=False)
save(main, "mainBgImage@2x.png"); save(main, "mainBgImage@3x.png")
PASS_BLOBS = [
    (0.50, 0.02, 0.70, (248, 214, 236), 255),
    (0.22, 0.50, 0.52, (196, 224, 247), 230),
    (0.85, 0.45, 0.52, (216, 202, 242), 225),
    (0.55, 1.00, 0.60, (236, 208, 240), 235),
]
passbg = make_bg((846, 846), PASS_BLOBS, (214, 206, 240), 4, 4, seed=3, checker=False)
save(passbg, "passcodeBgImage@2x.png"); save(passbg, "passcodeBgImage@3x.png")
save(passbg.resize((375, 375), Image.LANCZOS), "passcodeBgImage.png")


def tabbar(size):
    # soft pink gradient, no checker edge (checker is chatroom-only now)
    return dreamy(size, [(0.5, 0.0, 0.8, (250, 222, 240), 255),
                         (0.5, 1.0, 0.8, (246, 212, 234), 255)], (248, 216, 236))
save(tabbar((750, 106)), "maintabBgImage@2x.png")
save(tabbar((1125, 159)), "maintabBgImage@3x.png")


# ===========================================================================
# Tab icons  (normal = muted, Selected = pink)   2x:76x58  3x:156x118
# ===========================================================================
print("tab icons...")
TABS = {
    "maintabIcoFriends": (PERSON, pal_mono),
    "maintabIcoChats":   (HEART, lambda c: pal_heart(c)),
    "maintabIcoBrowse":  (CLOUD, lambda c: {"o": darken(c, 0.8), "W": c}),
    "maintabIcoFind":    (PHONE, lambda c: {"o": darken(c, 0.8), "W": c, "b": darken(c, 0.7)}),
    "maintabIcoPiccoma": (BUTTERFLY, lambda c: pal_butterfly(c, darken(c, 0.7))),
    "maintabIcoGame":    (STAR5, lambda c: pal_star(c)),
    "maintabIcoMore":    (GRID, lambda c: {"o": c}),
}
for name, (rows, palfn) in TABS.items():
    for scale, suf in ((1, "@2x"), (2, "@3x")):
        w, h = 76 * scale, 58 * scale
        sprite_canvas(rows, palfn(MUTED), w, h, ratio=0.72).save(
            os.path.join(IMG, f"{name}{suf}.png"))
        sprite_canvas(rows, palfn(ACCENT), w, h, ratio=0.72).save(
            os.path.join(IMG, f"{name}Selected{suf}.png"))


# ===========================================================================
# Rounded-square pixel avatar tiles (theme icon + default profiles)
# ===========================================================================
print("icons & profiles...")
def tile(rows, palette, px, bg=(225, 211, 242), ratio=0.62):
    s = 4
    W = px * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, W - 1], radius=int(W * 0.26), fill=bg)
    spr = sprite_canvas(rows, palette, W, W, ratio=ratio)
    im.alpha_composite(spr)
    return im.resize((px, px), Image.LANCZOS)


# theme picker icon = pink pixel heart tile
tile(HEART, pal_heart(H_PINK), 162).save(os.path.join(IMG, "commonIcoTheme.png"))

# default profile images: heart / butterfly / cloud
PROFILES = [
    ("profileImg01", HEART, pal_heart(H_PINK), (235, 214, 246)),
    ("profileImg02", BUTTERFLY, pal_butterfly(BFLY_CYAN, darken(BFLY_CYAN, 0.7)), (214, 232, 248)),
    ("profileImg03", CLOUD, pal_cloud(), (224, 224, 248)),
]
for name, rows, pal, bg in PROFILES:
    t2 = tile(rows, pal, 240, bg=bg)
    t2.save(os.path.join(IMG, f"{name}@2x.png"))
    t2.save(os.path.join(IMG, f"{name}@3x.png"))


def add_friend(w, h):
    s = 4
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    spr = sprite_canvas(PERSON, pal_mono(ACCENT), int(w * s * 0.8), h * s, ratio=0.78)
    im.alpha_composite(spr, (0, 0))
    cx, cy, r = int(w * s * 0.82), int(h * s * 0.30), int(h * s * 0.16)
    lw = int(h * s * 0.09)
    d.line([cx - r, cy, cx + r, cy], fill=ACCENT, width=lw)
    d.line([cx, cy - r, cx, cy + r], fill=ACCENT, width=lw)
    return im.resize((w, h), Image.LANCZOS)
add_friend(84, 68).save(os.path.join(IMG, "findBtnAddFriend@2x.png"))
add_friend(126, 102).save(os.path.join(IMG, "findBtnAddFriend@3x.png"))


# ===========================================================================
# Passcode bullets (4 colored hearts) + keypad pressed highlight
# ===========================================================================
print("passcode...")
BULLET_COLORS = [H_PURPLE, H_PINK, H_BLUE, H_GREEN]
for i, col in enumerate(BULLET_COLORS, start=1):
    empty = sprite_canvas(HEART_OUTLINE, pal_heart_outline(darken(col, 0.85)), 132, 132, ratio=0.62)
    full = sprite_canvas(HEART, pal_heart(col), 132, 132, ratio=0.62)
    for suf in ("@2x", "@3x"):
        empty.save(os.path.join(IMG, f"passcodeImgCode0{i}{suf}.png"))
        full.save(os.path.join(IMG, f"passcodeImgCode0{i}Selected{suf}.png"))


def keypad(px):
    s = 4
    W = px * s
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([int(W * 0.08)] * 2 + [int(W * 0.92)] * 2,
                               fill=(247, 210, 233, 230))
    return im.resize((px, px), Image.LANCZOS)
keypad(90).save(os.path.join(IMG, "passcodeKeypadPressed.png"))
keypad(120).save(os.path.join(IMG, "passcodeKeypadPressed@2x.png"))
keypad(180).save(os.path.join(IMG, "passcodeKeypadPressed@3x.png"))


# ===========================================================================
# Verification (9-slice stretch proof) — not shipped in the .ktheme
# ===========================================================================
print("verify...")
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
            tile_ = img.crop((sx0, sy0, sx1, sy1))
            out.alpha_composite(tile_.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)),
                                             Image.BICUBIC), (dx0, dy0))
    return out


send3 = _bubble_variant(SENT, 3)
cap3 = CAP * 3
verify = Image.new("RGBA", (860, 320), (242, 230, 248, 255))
x = 12
for (w, h) in [(BUB_W * 3, BUB_H * 3), (470, BUB_H * 3), (470, 270), (210, 270)]:
    verify.alpha_composite(nine_slice(send3, cap3, w, h), (x, 20))
    x += w + 12
verify.convert("RGB").save(os.path.join(PREV, "verify_stretch.png"))

print("done.")
