"""Generate an animated GIF diagram for Pattern 12: Iterative Refinement (Reflection).

Run with:
    uv run --offline --with pillow python 12_iterative_refinement/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–11)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Draft)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Self-Reflect)
SUCCESS = "#34D399"     # Emerald (Polished)
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BADGE_TEXT = "#082F49"


def load_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if mono:
        candidates = ["consolab.ttf" if bold else "consola.ttf", "DejaVuSansMono.ttf"]
    elif bold:
        candidates = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    else:
        candidates = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]

    for name in candidates:
        for base in [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")]:
            p = base / name
            if p.exists():
                return ImageFont.truetype(str(p), size * SCALE)
    return ImageFont.load_default()


FONT_TITLE = load_font(18, bold=True)
FONT_SUB = load_font(12, bold=False)
FONT_NODE = load_font(14, bold=True)
FONT_NODE_SUB = load_font(11, bold=False)
FONT_MONO = load_font(12, bold=True, mono=True)
FONT_SMALL_BOLD = load_font(10, bold=True)
FONT_STEP_TITLE = load_font(15, bold=True)
FONT_STEP_DESC = load_font(13, bold=False)


def s(v: float) -> int:
    return int(round(v * SCALE))


def draw_rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str,
    width: int = 2,
):
    x1, y1, x2, y2 = [s(v) for v in box]
    draw.rounded_rectangle([x1, y1, x2, y2], radius=s(radius), fill=fill, outline=outline, width=s(width))


def draw_centered_text(draw: ImageDraw.ImageDraw, cx: float, cy: float, text: str, font, fill: str):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((s(cx) - tw / 2, s(cy) - th / 2), text, font=font, fill=fill)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    p1: tuple[float, float],
    p2: tuple[float, float],
    color: str,
    width: int = 2,
    dot_t: float | None = None,
):
    x1, y1 = s(p1[0]), s(p1[1])
    x2, y2 = s(p2[0]), s(p2[1])
    draw.line([(x1, y1), (x2, y2)], fill=color, width=s(width))

    angle = math.atan2(y2 - y1, x2 - x1)
    head_len = s(9)
    head_ang = math.pi / 6
    ax1 = x2 - head_len * math.cos(angle - head_ang)
    ay1 = y2 - head_len * math.sin(angle - head_ang)
    ax2 = x2 - head_len * math.cos(angle + head_ang)
    ay2 = y2 - head_len * math.sin(angle + head_ang)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)

    if dot_t is not None:
        dx = x1 + (x2 - x1) * dot_t
        dy = y1 + (y2 - y1) * dot_t
        r = s(5)
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=TEXT, outline=color, width=s(2))


STEPS = [
    {
        "badge": "PASS 1 · DRAFT",
        "title": "initial_draft() writes a 130-word LinkedIn post",
        "desc": "Topic: 'Why choosing the right AI agent design pattern matters more than prompt engineering.'",
        "active_nodes": {0},
        "done_nodes": set(),
        "active_edge": "e01",
        "ref_active": False,
        "color": ACCENT,
    },
    {
        "badge": "PASS 2 · REFLECT",
        "title": "self_reflect() critiques the draft as a busy executive",
        "desc": "Lists 3 concrete weaknesses: jargon, buried hook, and weak closing question.",
        "active_nodes": {1},
        "done_nodes": {0},
        "active_edge": "e12",
        "ref_active": False,
        "color": AMBER,
    },
    {
        "badge": "PASS 3 · REFINE",
        "title": "refine_draft() rewrites using both draft + reflection",
        "desc": "Front-loads the hook, cuts buzzwords, and sharpens the CTA into state['polished'].",
        "active_nodes": {2},
        "done_nodes": {0, 1},
        "active_edge": None,
        "ref_active": True,
        "color": SUCCESS,
    },
    {
        "badge": "POLISHED",
        "title": "Sharper final LinkedIn post ready to publish",
        "desc": "Same agent, 3 structured passes — higher quality without needing a second critic agent.",
        "active_nodes": set(),
        "done_nodes": {0, 1, 2},
        "active_edge": None,
        "ref_active": False,
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 12: Iterative Refinement (Reflection)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Single Agent · 3 Self-Reflection Passes  (12_iterative_refinement/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Outer frame: Same Agent
    draw_rounded_box(draw, (32, 92, W - 32, 330), 14, BG, BORDER, width=1)
    draw.text((s(48), s(102)), "SAME AGENT  ·  3 PASSES", font=FONT_SMALL_BOLD, fill=MUTED)

    # 3 Pass boxes
    boxes = [
        (52, 130, 282, 266),
        (335, 130, 565, 266),
        (618, 130, 848, 266),
    ]
    labels = [
        ("1. Initial Draft", "initial_draft()", "130-word LinkedIn post", "(first rough pass)"),
        ("2. Self-Reflect", "self_reflect()", "Read as busy exec:", "jargon · hook · CTA"),
        ("3. Refine Draft", "refine_draft()", "Apply all 3 fixes", "→ polished post"),
    ]

    # Reference line: draft -> refine
    ref_color = SUCCESS if step["ref_active"] else BORDER
    ref_y = 296
    draw.line([(s(167), s(266)), (s(167), s(ref_y))], fill=ref_color, width=s(2))
    draw.line([(s(167), s(ref_y)), (s(733), s(ref_y))], fill=ref_color, width=s(2))
    draw_arrow(draw, (733, ref_y), (733, 268), color=ref_color, width=2)
    draw_centered_text(draw, 450, ref_y + 14, "refine_draft() reads both draft + reflection", FONT_NODE_SUB, ref_color if step["ref_active"] else MUTED)

    # Linear Edges
    for i, ename in enumerate(["e01", "e12"]):
        is_active = step["active_edge"] == ename
        is_done = i in step["done_nodes"]
        color = hi if is_active else (SUCCESS if is_done else BORDER)
        draw_arrow(
            draw,
            (boxes[i][2] + 2, 198),
            (boxes[i + 1][0] - 4, 198),
            color=color,
            width=3 if is_active else 2,
            dot_t=dot_t if is_active else None,
        )

    # Draw 3 Pass Boxes
    for i, (title, fn, d1, d2) in enumerate(labels):
        x1, y1, x2, y2 = boxes[i]
        cx = (x1 + x2) / 2
        is_active = i in step["active_nodes"]
        is_done = i in step["done_nodes"]
        outline = hi if is_active else (SUCCESS if is_done else BORDER)
        draw_rounded_box(draw, boxes[i], 12, CARD, outline, width=3 if is_active else 2)
        draw_centered_text(draw, cx, y1 + 26, title, FONT_NODE, TEXT)
        draw_centered_text(draw, cx, y1 + 52, fn, FONT_MONO, hi if is_active else (SUCCESS if is_done else ACCENT))
        draw_centered_text(draw, cx, y1 + 86, d1, FONT_NODE_SUB, MUTED)
        draw_centered_text(draw, cx, y1 + 106, d2, FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 204, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 128, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(220), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(410)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        if step["active_edge"]:
            for t in [0.15, 0.38, 0.62, 0.85]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(145)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1250)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1600)

    out_path = Path(__file__).resolve().parent / "12_iterative_refinement.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Saved {out_path} ({len(frames)} frames, {out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
