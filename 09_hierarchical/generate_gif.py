"""Generate an animated GIF diagram for Pattern 09: Hierarchical Task Decomposition.

Run with:
    uv run --offline --with pillow python 09_hierarchical/generate_gif.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–08)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Top-down delegation)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Dept leads / Leaf execution)
SUCCESS = "#34D399"     # Emerald (Roll-up Sign-Off)
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


def draw_dot(draw: ImageDraw.ImageDraw, x: float, y: float, color: str):
    r = s(5)
    draw.ellipse([s(x) - r, s(y) - r, s(x) + r, s(y) + r], fill=TEXT, outline=color, width=s(2))


STEPS = [
    {
        "badge": "1. TOP GOAL",
        "title": "L1 Director delegates 'Day-1 Readiness' to 3 leads",
        "desc": "Alex Chen (Senior Staff Engineer, Sydney HQ) is routed to IT, HR, and Facilities leads.",
        "dir_sub": "Goal: Day-1 Readiness (Alex Chen)",
        "active_level": 1,
        "edge_group": "l1_down",
        "color": ACCENT,
    },
    {
        "badge": "2. DEPT LEADS",
        "title": "L2 Department Leads break sub-goals into leaf tasks",
        "desc": "IT, HR, and Facilities leads each own 2 concrete onboarding subtasks.",
        "dir_sub": "Goal: Day-1 Readiness (Alex Chen)",
        "active_level": 2,
        "edge_group": "l2_down",
        "color": AMBER,
    },
    {
        "badge": "3. LEAF TASKS",
        "title": "L3 Leaf checklists execute across all 3 departments",
        "desc": "SSO, laptop, payroll, orientation, badge, and workstation tasks complete and roll up.",
        "dir_sub": "Goal: Day-1 Readiness (Alex Chen)",
        "active_level": 3,
        "edge_group": "l2_up",
        "color": AMBER,
    },
    {
        "badge": "4. ROLL-UP",
        "title": "L1 Director compiles final Day-1 Readiness Sign-Off",
        "desc": "top_level_rollup() merges it_report, hr_report, and facilities_report into one sign-off.",
        "dir_sub": "Day-1 Readiness Sign-Off Complete",
        "active_level": 1,
        "edge_group": "l1_up",
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    lvl = step["active_level"]
    eg = step["edge_group"]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 09: Hierarchical Task Decomposition", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "3-Level Org Tree: Executive → Dept Leads → Leaf Tasks  (09_hierarchical/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    cols = [164, 450, 736]

    # L1 <-> L2 connectors
    l1_active = eg in ("l1_down", "l1_up")
    c1 = hi if l1_active else BORDER
    w1 = 3 if l1_active else 2
    draw.line([(s(450), s(142)), (s(450), s(162))], fill=c1, width=s(w1))
    draw.line([(s(164), s(162)), (s(736), s(162))], fill=c1, width=s(w1))
    for cx in cols:
        draw.line([(s(cx), s(162)), (s(cx), s(182))], fill=c1, width=s(w1))
        if l1_active and dot_t is not None:
            y = 162 + 20 * dot_t if eg == "l1_down" else 182 - 20 * dot_t
            draw_dot(draw, cx, y, c1)

    # L2 <-> L3 connectors
    l2_active = eg in ("l2_down", "l2_up")
    c2 = hi if l2_active else BORDER
    w2 = 3 if l2_active else 2
    for cx in cols:
        draw.line([(s(cx), s(236)), (s(cx), s(262))], fill=c2, width=s(w2))
        if l2_active and dot_t is not None:
            y = 236 + 26 * dot_t if eg == "l2_down" else 262 - 26 * dot_t
            draw_dot(draw, cx, y, c2)

    # Level 1: Onboarding Director
    draw_rounded_box(draw, (280, 88, 620, 142), 12, CARD, hi if lvl == 1 else BORDER, width=3 if lvl == 1 else 2)
    draw_centered_text(draw, 450, 108, "L1: Onboarding Director", FONT_NODE, TEXT)
    draw_centered_text(draw, 450, 128, step["dir_sub"], FONT_NODE_SUB, hi if lvl == 1 else MUTED)

    # Level 2: Department Leads
    leads = [
        (164, "L2: IT Lead", "it_department_node"),
        (450, "L2: HR Lead", "hr_department_node"),
        (736, "L2: Facilities Lead", "facilities_node"),
    ]
    for cx, title, fn in leads:
        draw_rounded_box(draw, (cx - 118, 182, cx + 118, 236), 10, CARD, hi if lvl == 2 else BORDER, width=3 if lvl == 2 else 2)
        draw_centered_text(draw, cx, 200, title, FONT_NODE, TEXT)
        draw_centered_text(draw, cx, 220, fn, FONT_MONO, hi if lvl == 2 else ACCENT)

    # Level 3: Leaf Subtasks
    leaves = [
        (164, "L3: IT LEAVES", "• SSO/Okta & GitHub", "• Laptop & security keys"),
        (450, "L3: HR LEAVES", "• Contract & payroll", "• Compliance & orientation"),
        (736, "L3: FACILITIES LEAVES", "• Office access badge", "• Workstation & welcome kit"),
    ]
    for cx, tag, t1, t2 in leaves:
        draw_rounded_box(draw, (cx - 128, 262, cx + 128, 330), 10, CARD, hi if lvl == 3 else BORDER, width=3 if lvl == 3 else 2)
        draw_centered_text(draw, cx, 278, tag, FONT_SMALL_BOLD, hi if lvl == 3 else ACCENT)
        draw_centered_text(draw, cx, 298, t1, FONT_NODE_SUB, TEXT if lvl == 3 else MUTED)
        draw_centered_text(draw, cx, 316, t2, FONT_NODE_SUB, TEXT if lvl == 3 else MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 354, W - 32, 450), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 372, 188, 400), 6, hi, hi, width=1)
    draw_centered_text(draw, 120, 386, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(204), s(375)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(414)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx in range(len(STEPS)):
        for t in [0.15, 0.45, 0.75]:
            frames.append(render_frame(idx, dot_t=t))
            durations.append(160)
        frames.append(render_frame(idx, dot_t=None))
        durations.append(1400)

    out_path = Path(__file__).resolve().parent / "09_hierarchical.gif"
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
