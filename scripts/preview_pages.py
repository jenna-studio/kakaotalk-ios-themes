#!/usr/bin/env python3
"""Render mockups of KakaoTalk screens with the Pastel Bunny theme applied,
so you can see the theme without installing. Outputs preview/pages.png."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "theme", "Images")
PREV = os.path.join(ROOT, "preview")

W, H = 360, 740
PINK_HDR = (255, 215, 232)
TEXT = (92, 74, 84)
SUB = (169, 140, 153)
ACCENT = (255, 111, 163)


def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()


def load(name):
    return Image.open(os.path.join(IMG, name)).convert("RGBA")


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
            t = img.crop((sx0, sy0, sx1, sy1))
            out.alpha_composite(t.resize((max(1, dx1 - dx0), max(1, dy1 - dy0)),
                                         Image.BICUBIC), (dx0, dy0))
    return out


def header(d, title):
    d.rectangle([0, 0, W, 64], fill=PINK_HDR)
    d.text((20, 40), title, font=font(22, True), fill=TEXT, anchor="lm")


def statusbar(d):
    d.text((22, 14), "9:24", font=font(12, True), fill=TEXT, anchor="lm")
    d.text((W - 22, 14), "100% ▰", font=font(12), fill=TEXT, anchor="rm")


# --- Screen 1: Friends list -------------------------------------------------
def friends():
    bg = load("mainBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    s = bg.copy()
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, W, 64], fill=PINK_HDR)
    statusbar(d)
    d.text((20, 44), "Friends", font=font(22, True), fill=TEXT, anchor="lm")
    for ic in ("⌕", "+", "⚙"):
        pass
    prof = load("profileImg01@3x.png")
    rows = [("Apeach", "spring is here~", 96),
            ("Neo", "shopping today", 168),
            ("Ryan", "Bloom - Troye Sivan", 240),
            ("Tube", "see you tomorrow", 312),
            ("New friends!", "", 384)]
    # my profile (bigger)
    p = prof.resize((58, 58), Image.LANCZOS)
    s.alpha_composite(p, (20, 78))
    d.text((90, 96), "Me", font=font(17, True), fill=TEXT, anchor="lm")
    d.text((90, 116), "Pastel Bunny \U0001f430", font=font(12), fill=SUB, anchor="lm")
    d.line([20, 150, W - 20, 150], fill=(240, 215, 225))
    d.text((20, 168), "Favorites", font=font(12, True), fill=SUB, anchor="lm")
    y0 = 188
    for i, (nm, st, _) in enumerate(rows):
        y = y0 + i * 64
        pp = prof.resize((46, 46), Image.LANCZOS)
        s.alpha_composite(pp, (20, y))
        d.text((80, y + 14), nm, font=font(16, True), fill=TEXT, anchor="lm")
        if st:
            d.text((80, y + 34), st, font=font(12), fill=SUB, anchor="lm")
    return s


# --- Screen 2: Chatroom -----------------------------------------------------
def chatroom():
    bg = load("chatroomBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    s = bg.copy()
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, W, 64], fill=PINK_HDR)
    statusbar(d)
    d.text((W // 2, 44), "Bunny Friends", font=font(18, True), fill=TEXT, anchor="mm")
    send = load("chatroomBubbleSend01@3x.png")
    recv = load("chatroomBubbleReceive01@3x.png")
    cap = 60
    prof = load("profileImg01@3x.png").resize((40, 40), Image.LANCZOS)

    def bubble(text, side, y):
        ft = font(14)
        tw = int(d.textlength(text, font=ft))
        bw, bh = tw + 40, 62
        ty = y + int(bh * 0.60)          # body center (ears occupy the top)
        img = nine_slice(recv if side == "L" else send, cap, bw, bh)
        if side == "L":
            s.alpha_composite(prof, (14, y + 8))
            bx = 62
            s.alpha_composite(img, (bx, y))
            d.text((bx + bw // 2, ty), text, font=ft, fill=(65, 84, 76), anchor="mm")
            d.text((bx + bw + 6, y + bh - 8), "6:45", font=font(9), fill=SUB, anchor="lm")
        else:
            bx = W - 14 - bw
            s.alpha_composite(img, (bx, y))
            d.text((bx + bw // 2, ty), text, font=ft, fill=TEXT, anchor="mm")
            d.text((bx - 6, y + bh - 8), "6:45", font=font(9), fill=SUB, anchor="rm")

    d.text((62, 88), "Apeach", font=font(11), fill=SUB, anchor="lm")
    bubble("hi there!", "L", 100)
    bubble("how are you?", "L", 168)
    bubble("hello~ so good!", "R", 236)
    bubble("look, bunny bubbles", "R", 304)
    bubble("so cute!! \U0001f430", "L", 372)

    # input bar
    d.rectangle([0, H - 54, W, H], fill=(255, 233, 242))
    d.ellipse([14, H - 44, 46, H - 12], outline=(194, 132, 156), width=2)
    d.text((30, H - 28), "+", font=font(20), fill=(194, 132, 156), anchor="mm")
    d.rounded_rectangle([54, H - 44, W - 56, H - 12], radius=16, fill=(255, 255, 255))
    d.ellipse([W - 46, H - 44, W - 14, H - 12], fill=ACCENT)
    d.text((W - 30, H - 28), "↑", font=font(18, True), fill=(255, 255, 255), anchor="mm")
    return s


# --- Screen 3: Passcode -----------------------------------------------------
def passcode():
    bg = load("passcodeBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    s = bg.copy()
    d = ImageDraw.Draw(s)
    statusbar(d)
    d.text((W // 2, 150), "Passcode", font=font(22, True), fill=TEXT, anchor="mm")
    d.text((W // 2, 182), "Enter your KakaoTalk passcode.", font=font(12), fill=SUB, anchor="mm")
    dot_f = load("passcodeImgCode01Selected@3x.png").resize((26, 26), Image.LANCZOS)
    dot_e = load("passcodeImgCode01@3x.png").resize((26, 26), Image.LANCZOS)
    bx = W // 2 - 60
    for i in range(4):
        s.alpha_composite(dot_f if i < 2 else dot_e, (bx + i * 40, 214))
    # keypad
    keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "⌫"]]
    d.rectangle([0, H - 320, W, H], fill=(255, 227, 239))
    press = load("passcodeKeypadPressed@3x.png").resize((68, 68), Image.LANCZOS)
    for r, row in enumerate(keys):
        for c, k in enumerate(row):
            cx, cy = 60 + c * 120, H - 280 + r * 70
            if k == "5":
                s.alpha_composite(press, (cx - 34, cy - 34))
            if k:
                d.text((cx, cy), k, font=font(26), fill=TEXT, anchor="mm")
    return s


def main():
    screens = [("Friends", friends()), ("Chatroom", chatroom()), ("Passcode", passcode())]
    gap, pad, lab = 24, 24, 30
    total_w = pad * 2 + len(screens) * W + (len(screens) - 1) * gap
    canvas = Image.new("RGB", (total_w, H + pad * 2 + lab), (245, 240, 246))
    d = ImageDraw.Draw(canvas)
    x = pad
    for name, sc in screens:
        canvas.paste(sc.convert("RGB"), (x, pad + lab))
        d.text((x + W // 2, pad + lab // 2), name, font=font(18, True),
               fill=(120, 96, 110), anchor="mm")
        x += W + gap
    out = os.path.join(PREV, "pages.png")
    canvas.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
