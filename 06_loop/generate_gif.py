"""Generate an animated GIF diagram for Pattern 06: Loop (Bounded Retry).

Run with:
    uv run --offline --with pillow python 06_loop/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–05)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Normal flow)
ACCENT_SOFT = "#0284C7"
ERROR = "#F87171"       # Coral red (Test fail / retry)
AMBER = "#FBBF24"       # Amber (Attempt 2 fix)
SUCCESS = "#34D399"     # Emerald (Tests pass / END)
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
FONT_MONO = load_font(13, bold=True, mono=True)
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


STEPS = [
    {
        "badge": "ATTEMPT 1 · CODE",
        "title": "write_code() drafts slugify(text)  (attempts = 1)",
        "desc": "Generates initial Python implementation for slugify() from the spec.",
        "attempt": "Attempt 1 / 3",
        "test_status": "3 unit assertions",
        "active_nodes": {"write"},
        "active_edge": "wt",
        "color": ACCENT,
    },
    {
        "badge": "ATTEMPT 1 · FAIL",
        "title": "run_tests() fails: AssertionError on 'a---b'",
        "desc": "Captures the failure into state['test_error'] and sets passed = False.",
        "attempt": "Attempt 1 / 3",
        "test_status": "FAIL: AssertionError",
        "active_nodes": {"test"},
        "active_edge": "tg",
        "color": ERROR,
    },
    {
        "badge": "GATE · RETRY",
        "title": "should_continue() loops back to write_code()",
        "desc": "passed is False and attempts (1) < MAX_ATTEMPTS (3) → retry with test_error.",
        "attempt": "Attempt 1 / 3",
        "test_status": "FAIL: AssertionError",
        "active_nodes": {"gate"},
        "active_edge": "retry",
        "color": ERROR,
    },
    {
        "badge": "ATTEMPT 2 · FIX",
        "title": "write_code() patches regex using test_error  (attempts = 2)",
        "desc": "Fixes consecutive-hyphen collapsing based on the previous assertion error.",
        "attempt": "Attempt 2 / 3",
        "test_status": "Re-running tests...",
        "active_nodes": {"write"},
        "active_edge": "wt",
        "color": AMBER,
    },
    {
        "badge": "ATTEMPT 2 · PASS",
        "title": "run_tests() passes all 3 unit assertions!",
        "desc": "All 3 slugify() assertions succeed. Sets passed = True and clears test_error.",
        "attempt": "Attempt 2 / 3",
        "test_status": "PASS: 3 / 3",
        "active_nodes": {"test"},
        "active_edge": "tg",
        "color": SUCCESS,
    },
    {
        "badge": "GATE · EXIT",
        "title": "Exit condition met → END with verified code",
        "desc": "passed is True, so should_continue() exits cleanly without needing attempt 3.",
        "attempt": "Attempt 2 / 3",
        "test_status": "PASS: 3 / 3",
        "active_nodes": {"gate", "end"},
        "active_edge": "ge",
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
    draw.text((s(32), s(22)), "Pattern 06: Loop (Bounded Retry)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "write_code → run_tests → Exit Gate (MAX_ATTEMPTS = 3)  (06_loop/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Forward Edges
    edges = {
        "wt": ((236, 178), (296, 178)),
        "tg": ((502, 178), (562, 178)),
        "ge": ((714, 178), (760, 178)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Retry loop-back polyline: Gate bottom (638, 232) -> (638, 294) -> (134, 294) -> (134, 234)
    retry_active = active_edge == "retry"
    r_color = hi if retry_active else BORDER
    r_w = 3 if retry_active else 2
    draw.line([(s(638), s(232)), (s(638), s(294))], fill=r_color, width=s(r_w))
    draw.line([(s(638), s(294)), (s(134), s(294))], fill=r_color, width=s(r_w))
    draw_arrow(draw, (134, 294), (134, 236), color=r_color, width=r_w)
    if retry_active and dot_t is not None:
        # Animate dot along the bottom horizontal return segment
        dx = s(638 - (638 - 134) * dot_t)
        dy = s(294)
        r = s(5)
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=TEXT, outline=r_color, width=s(2))
    draw_centered_text(draw, 386, 312, "FAIL & attempts < 3  →  retry with test_error", FONT_NODE_SUB, r_color if retry_active else MUTED)

    # Node 1: write_code
    w_active = "write" in active_nodes
    draw_rounded_box(draw, (32, 122, 234, 232), 12, CARD, hi if w_active else BORDER, width=3 if w_active else 2)
    draw_centered_text(draw, 133, 150, "write_code()", FONT_MONO, hi if w_active else TEXT)
    draw_centered_text(draw, 133, 178, step["attempt"], FONT_SMALL_BOLD, hi if w_active else ACCENT)
    draw_centered_text(draw, 133, 204, "Generate slugify()", FONT_NODE_SUB, MUTED)

    # Node 2: run_tests
    t_active = "test" in active_nodes
    draw_rounded_box(draw, (300, 122, 500, 232), 12, CARD, hi if t_active else BORDER, width=3 if t_active else 2)
    draw_centered_text(draw, 400, 150, "run_tests()", FONT_MONO, hi if t_active else TEXT)
    draw_centered_text(draw, 400, 178, step["test_status"], FONT_SMALL_BOLD, hi if t_active else MUTED)
    draw_centered_text(draw, 400, 204, "exec() + 3 asserts", FONT_NODE_SUB, MUTED)

    # Node 3: Exit Gate
    g_active = "gate" in active_nodes
    draw_rounded_box(draw, (566, 126, 712, 230), 12, CARD, hi if g_active else BORDER, width=3 if g_active else 2)
    draw_centered_text(draw, 639, 154, "Exit Gate", FONT_NODE, TEXT)
    draw_centered_text(draw, 639, 180, "passed OR", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 639, 198, "attempts >= 3?", FONT_NODE_SUB, MUTED)

    # Node 4: END
    e_active = "end" in active_nodes
    draw_rounded_box(draw, (764, 140, 868, 216), 12, CARD, hi if e_active else BORDER, width=3 if e_active else 2)
    draw_centered_text(draw, 816, 168, "END", FONT_NODE, hi if e_active else TEXT)
    draw_centered_text(draw, 816, 192, "Verified", FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 210, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 131, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(226), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(410)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        for t in [0.15, 0.38, 0.62, 0.85]:
            frames.append(render_frame(idx, dot_t=t))
            durations.append(145)
        frames.append(render_frame(idx, dot_t=None))
        durations.append(1350)

    out_path = Path(__file__).resolve().parent / "06_loop.gif"
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
