"""Generate an animated GIF diagram for Pattern 04: Sequential (Prompt Chaining).

Run with:
    uv run --with pillow python 04_sequential/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–03)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Highlight for fact-check reference
SUCCESS = "#34D399"     # Emerald for verified final output
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
FONT_MONO = load_font(11, bold=True, mono=True)
FONT_SMALL_BOLD = load_font(11, bold=True)
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


STAGES = [
    ("1. Extract Facts", "brief → facts", "4 key claims from", "PulseTrace v2.0"),
    ("2. Draft Article", "facts → draft", "120-word launch", "announcement"),
    ("3. Brand Voice", "draft → branded", "Crisp, jargon-free", "engineering tone"),
    ("4. Fact-Check", "→ final_output", "Verify claims vs.", "original brief"),
]

STEPS = [
    {
        "badge": "STAGE 1 / 4",
        "title": "extract_facts: Distill product brief into 4 bullets",
        "desc": "Extracts launch date, latency alerts, 40% lower overhead, OTel support, and $99/mo pricing.",
        "active_nodes": {0},
        "done_nodes": set(),
        "active_edge": "e01",
        "ref_active": False,
        "color": ACCENT,
    },
    {
        "badge": "STAGE 2 / 4",
        "title": "draft_article: Write a 120-word launch announcement",
        "desc": "Consumes ONLY state['facts'] so the draft stays grounded and concise.",
        "active_nodes": {1},
        "done_nodes": {0},
        "active_edge": "e12",
        "ref_active": False,
        "color": ACCENT,
    },
    {
        "badge": "STAGE 3 / 4",
        "title": "apply_brand_voice: Polish tone without changing facts",
        "desc": "Rewrites state['draft'] into a confident, jargon-free engineering brand voice.",
        "active_nodes": {2},
        "done_nodes": {0, 1},
        "active_edge": "e23",
        "ref_active": False,
        "color": ACCENT,
    },
    {
        "badge": "STAGE 4 / 4",
        "title": "check_claims: Cross-check copy against original brief",
        "desc": "Compares state['branded'] back against state['brief'] to fix any unsupported claims.",
        "active_nodes": {3},
        "done_nodes": {0, 1, 2},
        "active_edge": None,
        "ref_active": True,
        "color": AMBER,
    },
    {
        "badge": "VERIFIED",
        "title": "Pipeline complete → final_output ready to publish",
        "desc": "Fixed linear order: no loops, no dynamic routing — predictable, testable, and auditable.",
        "active_nodes": set(),
        "done_nodes": {0, 1, 2, 3},
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
    draw.text((s(32), s(22)), "Pattern 04: Sequential (Prompt Chaining)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Fixed 4-Stage Assembly Line  (04_sequential/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # 4 Stage boxes geometry
    box_w, box_h = 182, 136
    gap = 36
    start_x = 32
    top_y = 118
    boxes = []
    for i in range(4):
        x1 = start_x + i * (box_w + gap)
        boxes.append((x1, top_y, x1 + box_w, top_y + box_h))

    # Reference line from Stage 1 bottom -> Stage 4 bottom (for fact-checking)
    ref_color = AMBER if step["ref_active"] else BORDER
    ref_y = 294
    x_left = boxes[0][0] + box_w // 2
    x_right = boxes[3][0] + box_w // 2
    draw.line([(s(x_left), s(top_y + box_h)), (s(x_left), s(ref_y))], fill=ref_color, width=s(2))
    draw.line([(s(x_left), s(ref_y)), (s(x_right), s(ref_y))], fill=ref_color, width=s(2))
    draw_arrow(draw, (x_right, ref_y), (x_right, top_y + box_h + 2), color=ref_color, width=2)
    draw_centered_text(draw, W / 2, ref_y + 16, "Original brief referenced for fact-checking", FONT_NODE_SUB, ref_color if step["ref_active"] else MUTED)

    # Linear Edges between boxes
    mid_y = top_y + box_h // 2
    for i in range(3):
        ename = f"e{i}{i+1}"
        is_active = step["active_edge"] == ename
        is_done = i in step["done_nodes"]
        color = hi if is_active else (SUCCESS if is_done else BORDER)
        draw_arrow(
            draw,
            (boxes[i][2] + 2, mid_y),
            (boxes[i + 1][0] - 4, mid_y),
            color=color,
            width=3 if is_active else 2,
            dot_t=dot_t if is_active else None,
        )

    # Draw Stage Boxes
    for i, (title, io_lbl, d1, d2) in enumerate(STAGES):
        x1, y1, x2, y2 = boxes[i]
        cx = (x1 + x2) / 2
        is_active = i in step["active_nodes"]
        is_done = i in step["done_nodes"]
        outline = hi if is_active else (SUCCESS if is_done else BORDER)
        draw_rounded_box(draw, (x1, y1, x2, y2), 12, CARD, outline, width=3 if is_active else 2)
        draw_centered_text(draw, cx, y1 + 28, title, FONT_NODE, TEXT)
        draw_centered_text(draw, cx, y1 + 54, io_lbl, FONT_MONO, hi if is_active else (SUCCESS if is_done else ACCENT))
        draw_centered_text(draw, cx, y1 + 86, d1, FONT_NODE_SUB, MUTED)
        draw_centered_text(draw, cx, y1 + 106, d2, FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 178, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 115, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(194), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(410)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        if step["active_edge"]:
            for t in [0.15, 0.38, 0.62, 0.85]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(140)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1250)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1600)

    out_path = Path(__file__).resolve().parent / "04_sequential.gif"
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
