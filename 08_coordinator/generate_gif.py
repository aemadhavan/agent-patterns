"""Generate an animated GIF diagram for Pattern 08: Coordinator (Orchestrator-Workers).

Run with:
    uv run --offline --with pillow python 08_coordinator/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–07)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Coordinator plan)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Specialist workers)
SUCCESS = "#34D399"     # Emerald (Coordinator assemble)
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
        "badge": "1. DECOMPOSE",
        "title": "coordinator_plan() writes 3 tailored specialist briefs",
        "desc": "Splits 'AI code review for FinTech' into sizing_brief, competitor_brief, and customer_brief.",
        "active_nodes": {"plan"},
        "active_edges": {"d1", "d2", "d3"},
        "color": ACCENT,
    },
    {
        "badge": "2. DELEGATE",
        "title": "3 role-specific analysts execute their assigned briefs",
        "desc": "Market Sizing Analyst, Competitive Intel, and UX Researcher each run with focused personas.",
        "active_nodes": {"w1", "w2", "w3"},
        "active_edges": set(),
        "color": AMBER,
    },
    {
        "badge": "3. REPORT BACK",
        "title": "Workers return structured findings to the Coordinator",
        "desc": "sizing_result, competitor_result, and customer_result converge on coordinator_assemble.",
        "active_nodes": {"w1", "w2", "w3"},
        "active_edges": {"r1", "r2", "r3"},
        "color": AMBER,
    },
    {
        "badge": "4. ASSEMBLE",
        "title": "coordinator_assemble() produces the executive report",
        "desc": "Acting as Principal Research Director, the Coordinator merges all 3 sections into one report.",
        "active_nodes": {"asm"},
        "active_edges": set(),
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    active_nodes = step["active_nodes"]
    active_edges = step["active_edges"]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 08: Coordinator (Orchestrator-Workers)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Decompose into Tailored Briefs → Specialist Workers → Assemble  (08_coordinator/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "d1": ((222, 206), (314, 128)),
        "d2": ((222, 206), (314, 206)),
        "d3": ((222, 206), (314, 284)),
        "r1": ((586, 128), (674, 206)),
        "r2": ((586, 206), (674, 206)),
        "r3": ((586, 284), (674, 206)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name in active_edges
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node: Coordinator Plan
    p_active = "plan" in active_nodes
    draw_rounded_box(draw, (32, 148, 220, 264), 12, CARD, hi if p_active else BORDER, width=3 if p_active else 2)
    draw_centered_text(draw, 126, 174, "Coordinator", FONT_NODE, TEXT)
    draw_centered_text(draw, 126, 196, "coordinator_plan", FONT_MONO, hi if p_active else ACCENT)
    draw_centered_text(draw, 126, 222, "Writes 3 tailored", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 126, 240, "specialist briefs", FONT_NODE_SUB, MUTED)

    # 3 Specialist Workers
    workers = [
        ("w1", 96, "sizing_worker()", "TAM/SAM/SOM brief"),
        ("w2", 174, "competitor_worker()", "Top 3 rivals brief"),
        ("w3", 252, "customer_worker()", "Buyer pain points brief"),
    ]
    for key, y1, fn_name, desc in workers:
        w_active = key in active_nodes
        outline = hi if w_active else BORDER
        draw_rounded_box(draw, (318, y1, 582, y1 + 64), 12, CARD, outline, width=3 if w_active else 2)
        draw_centered_text(draw, 450, y1 + 22, fn_name, FONT_MONO, hi if w_active else TEXT)
        draw_centered_text(draw, 450, y1 + 44, desc, FONT_NODE_SUB, MUTED)

    # Node: Coordinator Assemble
    a_active = "asm" in active_nodes
    draw_rounded_box(draw, (678, 148, 868, 264), 12, CARD, hi if a_active else BORDER, width=3 if a_active else 2)
    draw_centered_text(draw, 773, 174, "Coordinator", FONT_NODE, TEXT)
    draw_centered_text(draw, 773, 196, "assemble", FONT_MONO, SUCCESS if a_active else ACCENT)
    draw_centered_text(draw, 773, 222, "Principal Director", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 773, 240, "Executive Report", FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 198, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 125, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(214), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(410)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        if step["active_edges"]:
            for t in [0.15, 0.38, 0.62, 0.85]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(150)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1300)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1550)

    out_path = Path(__file__).resolve().parent / "08_coordinator.gif"
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
