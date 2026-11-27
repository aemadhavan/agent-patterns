"""Generate an animated GIF diagram for Pattern 15: Elephant-Goldfish Model.

Run with:
    uv run --offline --with pillow python 15_elephant_goldfish/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–14)
BG = "#0F172A"
CARD = "#1E293B"
INNER = "#0F172A"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Elephant)
ACCENT_SOFT = "#0284C7"
ERROR = "#F87171"       # Coral red (Goldfish REVISE)
AMBER = "#FBBF24"       # Amber (Context Firewall / Revise)
SUCCESS = "#34D399"     # Emerald (APPROVED)
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
        "badge": "1. BRAINSTORM",
        "title": "Elephant brainstorms webhook architecture & trade-offs",
        "desc": "Accumulates goals, rate limits, HMAC signing, and DLQ edge cases in elephant_history.",
        "el_hist": "Brainstorm + trade-offs",
        "el_round": "Drafting v1...",
        "gf_verdict": "Verdict: waiting",
        "active_nodes": {"elephant"},
        "active_edge": None,
        "color": ACCENT,
    },
    {
        "badge": "2. DRAFT v1",
        "title": "Elephant writes spec v1 → crosses Context Firewall",
        "desc": "ONLY state['spec'] crosses to Goldfish; all brainstorming notes stay behind the wall.",
        "el_hist": "Brainstorm + Draft v1",
        "el_round": "Round 1 / 3",
        "gf_verdict": "Cold-reading v1...",
        "active_nodes": {"elephant"},
        "active_edge": "eg",
        "color": ACCENT,
    },
    {
        "badge": "3. COLD READ",
        "title": "Goldfish exposes unstated assumptions → REVISE",
        "desc": "With zero prior memory, Goldfish catches gaps the Elephant took for granted.",
        "el_hist": "Brainstorm + Draft v1",
        "el_round": "Round 1 / 3",
        "gf_verdict": "Verdict: REVISE",
        "active_nodes": {"goldfish"},
        "active_edge": "ge",
        "color": ERROR,
    },
    {
        "badge": "4. REVISE v2",
        "title": "Elephant folds critique into history & ships Draft v2",
        "desc": "Closes every blocking gap using full memory + critique, then sends v2 across the wall.",
        "el_hist": "+ Review v1 + Draft v2",
        "el_round": "Round 2 / 3",
        "gf_verdict": "Cold-reading v2...",
        "active_nodes": {"elephant"},
        "active_edge": "eg",
        "color": AMBER,
    },
    {
        "badge": "5. APPROVED",
        "title": "Goldfish cold-reads v2 with zero gaps → APPROVED",
        "desc": "A stateless reader with zero context can implement v2 without guessing — spec is ready!",
        "el_hist": "Full history preserved",
        "el_round": "Round 2 / 3 · Done",
        "gf_verdict": "Verdict: APPROVED",
        "active_nodes": {"goldfish"},
        "active_edge": None,
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    active_nodes = step["active_nodes"]
    active_edge = step["active_edge"]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 15: Elephant-Goldfish Model", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Context-Rich Drafter + Stateless Cold-Read Reviewer  (15_elephant_goldfish/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Vertical Context Firewall
    for y in range(114, 332, 14):
        draw.line([(s(450), s(y)), (s(450), s(min(y + 7, 332)))], fill=AMBER, width=s(2))
    draw_rounded_box(draw, (374, 86, 526, 112), 6, CARD, AMBER, width=1)
    draw_centered_text(draw, 450, 99, "CONTEXT FIREWALL", FONT_SMALL_BOLD, AMBER)

    # Edges
    edges = {
        "eg": ((334, 174), (562, 174)),
        "ge": ((562, 264), (334, 264)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    draw_centered_text(draw, 450, 156, "ONLY spec (0 history)", FONT_SMALL_BOLD, hi if active_edge == "eg" else MUTED)
    draw_centered_text(draw, 450, 282, "REVISE: cold-read gaps", FONT_SMALL_BOLD, hi if active_edge == "ge" else MUTED)

    # Left: Elephant (Full Memory)
    e_active = "elephant" in active_nodes
    draw_rounded_box(draw, (32, 118, 330, 324), 12, CARD, hi if e_active else BORDER, width=3 if e_active else 2)
    draw_centered_text(draw, 181, 144, "Elephant (Full Memory)", FONT_NODE, TEXT)
    draw_centered_text(draw, 181, 166, "brainstorm + draft", FONT_MONO, hi if e_active else ACCENT)
    draw_rounded_box(draw, (50, 184, 312, 306), 8, INNER, hi if e_active else BORDER, width=1)
    draw_centered_text(draw, 181, 204, "ACCUMULATED HISTORY", FONT_SMALL_BOLD, ACCENT)
    draw_centered_text(draw, 181, 232, step["el_hist"], FONT_NODE_SUB, TEXT if e_active else MUTED)
    draw_centered_text(draw, 181, 256, step["el_round"], FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 181, 284, "Remembers every round", FONT_NODE_SUB, MUTED)

    # Right: Goldfish (Zero Memory)
    g_active = "goldfish" in active_nodes
    draw_rounded_box(draw, (566, 118, 868, 324), 12, CARD, hi if g_active else BORDER, width=3 if g_active else 2)
    draw_centered_text(draw, 717, 144, "Goldfish (Zero Memory)", FONT_NODE, TEXT)
    draw_centered_text(draw, 717, 166, "goldfish_review()", FONT_MONO, hi if g_active else ACCENT)
    draw_rounded_box(draw, (584, 184, 850, 306), 8, INNER, hi if g_active else BORDER, width=1)
    draw_centered_text(draw, 717, 204, "STATELESS COLD READ", FONT_SMALL_BOLD, AMBER)
    draw_centered_text(draw, 717, 232, "Sees ONLY standalone spec", FONT_NODE_SUB, TEXT if g_active else MUTED)
    draw_centered_text(draw, 717, 256, "Exposes hidden assumptions", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 717, 284, step["gf_verdict"], FONT_SMALL_BOLD, hi if g_active else ACCENT)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 202, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 127, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(218), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
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
            durations.append(1300)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1550)

    out_path = Path(__file__).resolve().parent / "15_elephant_goldfish.gif"
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
