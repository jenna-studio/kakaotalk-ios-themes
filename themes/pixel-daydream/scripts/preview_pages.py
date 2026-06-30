#!/usr/bin/env python3
"""Render mockups of KakaoTalk screens with the Pixel Daydream theme applied,
so you can see the look without installing. Outputs preview/pages.png,
preview/preview.png and preview/thumbnail.png. Uses the theme's real assets."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "Images")
PREV = os.path.join(ROOT, "preview")

W, H = 360, 740
HDR = (247, 217, 238)
TEXT = (106, 90, 122)
SUB = (156, 138, 182)
ACCENT = (240, 106, 160)
CAP3 = 22 * 3


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


def statusbar(d):
    d.text((22, 16), "9:41", font=font(13, True), fill=TEXT, anchor="lm")
    d.text((W - 22, 16), "100% ▰", font=font(12), fill=TEXT, anchor="rm")


# --- Chatroom ---------------------------------------------------------------
def chatroom():
    s = load("chatroomBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, W, 64], fill=HDR)
    statusbar(d)
    d.text((W // 2, 44), "Jenna \U0001f49c", font=font(18, True), fill=TEXT, anchor="mm")
    send = load("chatroomBubbleSend01@3x.png")
    recv = load("chatroomBubbleReceive01@3x.png")
    prof = load("profileImg01@3x.png").resize((40, 40), Image.LANCZOS)

    def bubble(text, side, y):
        ft = font(13)
        tw = int(d.textlength(text, font=ft))
        bw, bh = max(96, tw + 44), 70
        ty = y + int(bh * 0.66)          # text sits in the body, below title bar
        img = nine_slice(recv if side == "L" else send, CAP3, bw, bh)
        if side == "L":
            s.alpha_composite(prof, (12, y + 12))
            bx = 60
            s.alpha_composite(img, (bx, y))
            d.text((bx + bw // 2, ty), text, font=ft, fill=(107, 74, 96), anchor="mm")
            d.text((bx + bw + 6, y + bh - 8), "9:20", font=font(9), fill=SUB, anchor="lm")
        else:
            bx = W - 14 - bw
            s.alpha_composite(img, (bx, y))
            d.text((bx + bw // 2, ty), text, font=ft, fill=(69, 69, 110), anchor="mm")
            d.text((bx - 6, y + bh - 8), "9:21", font=font(9), fill=SUB, anchor="rm")

    d.text((60, 92), "Jenna \U0001f49c", font=font(11), fill=SUB, anchor="lm")
    bubble("Hey! How was your day?", "L", 104)
    bubble("Wanna grab coffee tomorrow?", "L", 184)
    bubble("It was great!", "R", 264)
    bubble("Yes please!", "R", 344)

    # input bar
    d.rectangle([0, H - 56, W, H], fill=(251, 221, 238))
    d.ellipse([14, H - 46, 46, H - 14], outline=(182, 139, 198), width=2)
    d.text((30, H - 30), "+", font=font(20), fill=(182, 139, 198), anchor="mm")
    d.rounded_rectangle([54, H - 46, W - 56, H - 14], radius=16, fill=(255, 255, 255))
    d.text((66, H - 30), "Let's meet at 2pm ☁", font=font(11), fill=(150, 130, 170), anchor="lm")
    d.ellipse([W - 46, H - 46, W - 14, H - 14], fill=ACCENT)
    d.text((W - 30, H - 30), "♥", font=font(15), fill=(255, 255, 255), anchor="mm")
    return s


# --- Chats list -------------------------------------------------------------
def chats():
    s = load("mainBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, W, 64], fill=HDR)
    statusbar(d)
    d.text((20, 44), "Chats", font=font(22, True), fill=TEXT, anchor="lm")
    avatars = ["profileImg01@3x.png", "profileImg02@3x.png", "profileImg03@3x.png",
               "profileImg01@3x.png", "profileImg02@3x.png", "profileImg03@3x.png"]
    rows = [("Jenna \U0001f49c", "See you tomorrow!", "9:21 PM", "2"),
            ("Besties \U0001f495", "Soojin: Hahaha same", "8:45 PM", "5"),
            ("Mom \U0001f338", "Don't forget to eat!", "8:30 PM", "1"),
            ("Study Group \U0001f4da", "Alex: I'll send the notes!", "7:12 PM", "3"),
            ("Archive ☁", "Photo", "Yesterday", ""),
            ("KakaoTalk \U0001f98b", "Welcome to KakaoTalk!", "Yesterday", "")]
    y0 = 84
    for i, (nm, msg, t, badge) in enumerate(rows):
        y = y0 + i * 96
        av = load(avatars[i]).resize((56, 56), Image.LANCZOS)
        s.alpha_composite(av, (18, y))
        d.text((86, y + 16), nm, font=font(15, True), fill=TEXT, anchor="lm")
        d.text((86, y + 40), msg, font=font(12), fill=SUB, anchor="lm")
        d.text((W - 18, y + 14), t, font=font(10), fill=SUB, anchor="rm")
        if badge:
            d.ellipse([W - 40, y + 32, W - 18, y + 54], fill=ACCENT)
            d.text((W - 29, y + 43), badge, font=font(11, True), fill=(255, 255, 255), anchor="mm")
    # tab bar
    TBH = 64
    s.alpha_composite(load("maintabBgImage@3x.png").resize((W, TBH), Image.LANCZOS), (0, H - TBH))
    order = [("Friends", "maintabIcoFriends", False), ("Chats", "maintabIcoChats", True),
             ("OpenChat", "maintabIcoBrowse", False), ("Calls", "maintabIcoFind", False),
             ("More", "maintabIcoMore", False)]
    slot = W // len(order)
    for i, (lab, key, on) in enumerate(order):
        suf = "Selected@3x.png" if on else "@3x.png"
        ic = load(key + suf).resize((34, 26), Image.LANCZOS)
        s.alpha_composite(ic, (i * slot + (slot - 34) // 2, H - TBH + 8))
        d.text((i * slot + slot // 2, H - 12), lab, font=font(9),
               fill=ACCENT if on else SUB, anchor="mm")
    return s


# --- Passcode ---------------------------------------------------------------
def passcode():
    s = load("passcodeBgImage@3x.png").resize((W, H), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(s)
    statusbar(d)
    d.text((W // 2, 150), "Enter Passcode", font=font(22, True), fill=TEXT, anchor="mm")
    d.text((W // 2, 184), "Please enter your passcode.", font=font(12), fill=SUB, anchor="mm")
    bx = W // 2 - 84
    for i in range(4):
        dot = load(f"passcodeImgCode0{i+1}Selected@3x.png").resize((40, 40), Image.LANCZOS)
        s.alpha_composite(dot, (bx + i * 56, 214))
    keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "⌫"]]
    press = load("passcodeKeypadPressed@3x.png").resize((70, 70), Image.LANCZOS)
    for r, row in enumerate(keys):
        for c, k in enumerate(row):
            cx, cy = 70 + c * 110, 360 + r * 84
            if k == "5":
                s.alpha_composite(press, (cx - 35, cy - 35))
            if k:
                d.text((cx, cy), k, font=font(30), fill=(138, 111, 176), anchor="mm")
    return s


def main():
    screens = [("Chats", chats()), ("Chatroom", chatroom()), ("Passcode", passcode())]
    gap, pad, lab = 24, 24, 30
    total_w = pad * 2 + len(screens) * W + (len(screens) - 1) * gap
    canvas = Image.new("RGB", (total_w, H + pad * 2 + lab), (244, 238, 248))
    d = ImageDraw.Draw(canvas)
    x = pad
    for name, sc in screens:
        canvas.paste(sc.convert("RGB"), (x, pad + lab))
        d.text((x + W // 2, pad + lab // 2), name, font=font(18, True),
               fill=(120, 96, 130), anchor="mm")
        x += W + gap
    canvas.save(os.path.join(PREV, "pages.png"))
    chatroom().convert("RGB").save(os.path.join(PREV, "preview.png"))
    load("commonIcoTheme.png").convert("RGB").save(os.path.join(PREV, "thumbnail.png"))
    print("wrote preview/pages.png, preview/preview.png, preview/thumbnail.png")


if __name__ == "__main__":
    main()
