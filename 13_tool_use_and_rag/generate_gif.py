"""Generate an animated GIF diagram for Pattern 13: Tool Use and RAG (The Grounded Agent).

Run with:
    uv run --offline --with pillow python 13_tool_use_and_rag/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–12)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Live Data)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (RAG & Code Math)
SUCCESS = "#34D399"     # Emerald (Cited Answer)
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


STEPS = [
    {
        "badge": "1. QUERY",
        "title": "User asks a high-stakes finance & policy question",
        "desc": '"Can we afford a $4,800 annual analytics software purchase today, and who must approve?"',
        "active_nodes": {"user"},
        "active_edge": "in",
        "color": ACCENT,
    },
    {
        "badge": "2. LIVE DATA",
        "title": "Calls get_finance_snapshot() for real-time balances",
        "desc": "Fetches live cash on hand and upcoming payables instead of guessing from memory.",
        "active_nodes": {"agent", "t1"},
        "active_edge": "t1",
        "color": ACCENT,
    },
    {
        "badge": "3. POLICY RAG",
        "title": "Calls search_company_policy() for 2026 approval rules",
        "desc": "Retrieves procurement policy ID, minimum cash buffer rule, and approver threshold.",
        "active_nodes": {"agent", "t2"},
        "active_edge": "t2",
        "color": AMBER,
    },
    {
        "badge": "4. EXACT MATH",
        "title": "Calls calculate_expression() to compute remaining buffer",
        "desc": "Runs deterministic code (cash - payables - 4800) so the LLM never hallucinates math.",
        "active_nodes": {"agent", "t3"},
        "active_edge": "t3",
        "color": AMBER,
    },
    {
        "badge": "5. CITED REPLY",
        "title": "Returns a grounded, auditable answer with exact citations",
        "desc": "Combines live figures, exact cash buffer, and the cited policy ID + required approver.",
        "active_nodes": {"agent", "user"},
        "active_edge": "out",
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
    draw.text((s(32), s(22)), "Pattern 13: Tool Use and RAG (The Grounded Agent)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Live Data + Policy RAG + Deterministic Math  (13_tool_use_and_rag/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "in": ((214, 192), (288, 192)),
        "out": ((288, 222), (214, 222)),
        "t1": ((506, 206), (594, 128)),
        "t2": ((506, 206), (594, 206)),
        "t3": ((506, 206), (594, 284)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node: User Query
    u_active = "user" in active_nodes
    draw_rounded_box(draw, (32, 152, 212, 260), 12, CARD, hi if u_active else BORDER, width=3 if u_active else 2)
    draw_centered_text(draw, 122, 178, "Finance Query", FONT_NODE, TEXT)
    draw_centered_text(draw, 122, 202, '"Afford $4,800', FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 122, 220, 'purchase + who', FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 122, 238, 'approves?"', FONT_NODE_SUB, MUTED)

    # Node: Grounded Agent
    a_active = "agent" in active_nodes
    draw_rounded_box(draw, (292, 138, 504, 274), 12, CARD, hi if a_active else BORDER, width=3 if a_active else 2)
    draw_centered_text(draw, 398, 166, "Grounded Agent", FONT_NODE, TEXT)
    draw_centered_text(draw, 398, 190, "NEVER GUESS", FONT_SMALL_BOLD, hi if a_active else ACCENT)
    draw_centered_text(draw, 398, 216, "Verify live cash,", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 398, 234, "policy ID & exact", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 398, 252, "buffer in code", FONT_NODE_SUB, MUTED)

    # 3 Grounding Tools
    tools = [
        ("t1", 96, "get_finance_snapshot()", "LIVE DATA · Cash & payables"),
        ("t2", 174, "search_company_policy()", "RAG · 2026 procurement rules"),
        ("t3", 252, "calculate_expression()", "CODE MATH · Exact cash buffer"),
    ]
    for key, y1, fn, desc in tools:
        t_active = key in active_nodes
        outline = hi if t_active else BORDER
        draw_rounded_box(draw, (598, y1, 868, y1 + 64), 12, CARD, outline, width=3 if t_active else 2)
        draw_centered_text(draw, 733, y1 + 22, fn, FONT_MONO, hi if t_active else TEXT)
        draw_centered_text(draw, 733, y1 + 44, desc, FONT_NODE_SUB, MUTED)

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

    for idx in range(len(STEPS)):
        for t in [0.15, 0.38, 0.62, 0.85]:
            frames.append(render_frame(idx, dot_t=t))
            durations.append(145)
        frames.append(render_frame(idx, dot_t=None))
        durations.append(1300)

    out_path = Path(__file__).resolve().parent / "13_tool_use_and_rag.gif"
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
