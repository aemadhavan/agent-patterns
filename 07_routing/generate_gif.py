"""Generate an animated GIF diagram for Pattern 07: Routing (Conditional Switchboard).

Run with:
    uv run --offline --with pillow python 07_routing/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–06)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Input & Classifier)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Route decision)
SUCCESS = "#34D399"     # Emerald (Active specialist)
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
DIM = "#475569"
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
        "badge": "1. INPUT",
        "title": "Customer submits a billing complaint",
        "desc": '"I was double-charged $49 on my November invoice. Can you refund the duplicate charge?"',
        "route_txt": "route = ?",
        "active_nodes": {"msg"},
        "active_edge": "in",
        "color": ACCENT,
    },
    {
        "badge": "2. CLASSIFY",
        "title": 'classify_request() outputs a single label: "billing"',
        "desc": "Inspects the message and sets state['route'] = 'billing' (defaults to 'technical' if unknown).",
        "route_txt": 'route = "billing"',
        "active_nodes": {"router"},
        "active_edge": None,
        "color": AMBER,
    },
    {
        "badge": "3. ROUTE",
        "title": "Conditional edge activates ONLY billing_agent()",
        "desc": "Unlike Parallel (all 3 run), Routing sends traffic down ONE path — the other 2 stay idle.",
        "route_txt": 'route = "billing"',
        "active_nodes": {"router", "bill"},
        "active_edge": "bill",
        "color": SUCCESS,
    },
    {
        "badge": "4. SPECIALIST",
        "title": "billing_agent() resolves the refund & exits to END",
        "desc": "Each specialist keeps a focused prompt instead of one bloated prompt handling everything.",
        "route_txt": 'route = "billing"',
        "active_nodes": {"bill"},
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
    draw.text((s(32), s(22)), "Pattern 07: Routing (Conditional Switchboard)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Classify → Activate 1 of 3 Specialists  (07_routing/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "in": ((222, 206), (294, 206)),
        "bill": ((512, 206), (608, 128)),
        "tech": ((512, 206), (608, 206)),
        "ret": ((512, 206), (608, 284)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node: Customer Message
    m_active = "msg" in active_nodes
    draw_rounded_box(draw, (32, 160, 220, 252), 12, CARD, hi if m_active else BORDER, width=3 if m_active else 2)
    draw_centered_text(draw, 126, 184, "Customer Message", FONT_NODE, TEXT)
    draw_centered_text(draw, 126, 208, '"Double-charged $49', FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 126, 226, 'on Nov invoice"', FONT_NODE_SUB, MUTED)

    # Node: Classifier Router
    r_active = "router" in active_nodes
    draw_rounded_box(draw, (298, 148, 510, 264), 12, CARD, hi if r_active else BORDER, width=3 if r_active else 2)
    draw_centered_text(draw, 404, 178, "classify_request()", FONT_MONO, hi if r_active else TEXT)
    draw_centered_text(draw, 404, 208, step["route_txt"], FONT_SMALL_BOLD, hi if r_active else ACCENT)
    draw_centered_text(draw, 404, 236, "Pick 1 of 3 specialists", FONT_NODE_SUB, MUTED)

    # 3 Specialist Branches
    specialists = [
        ("bill", 96, "billing_agent()", "Refunds & invoices"),
        ("tech", 174, "technical_agent()", "Troubleshooting (idle)"),
        ("ret", 252, "retention_handoff()", "Human escalation (idle)"),
    ]
    for key, y1, fn_name, desc in specialists:
        s_active = key in active_nodes
        outline = hi if s_active else BORDER
        draw_rounded_box(draw, (612, y1, 868, y1 + 64), 12, CARD, outline, width=3 if s_active else 2)
        draw_centered_text(draw, 740, y1 + 22, fn_name, FONT_MONO, hi if s_active else (TEXT if key == "bill" else DIM))
        draw_centered_text(draw, 740, y1 + 44, desc, FONT_NODE_SUB, MUTED if s_active else DIM)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 192, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 122, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(208), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(410)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        if step["active_edge"]:
            for t in [0.15, 0.38, 0.62, 0.85]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(150)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1300)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1550)

    out_path = Path(__file__).resolve().parent / "07_routing.gif"
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
