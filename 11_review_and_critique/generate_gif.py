"""Generate an animated GIF diagram for Pattern 11: Review and Critique (Evaluator-Optimizer).

Run with:
    uv run --offline --with pillow python 11_review_and_critique/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–10)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Draft)
ACCENT_SOFT = "#0284C7"
ERROR = "#F87171"       # Coral red (REVISE feedback)
AMBER = "#FBBF24"       # Amber (Round 2 revision)
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
        "badge": "ROUND 1 · DRAFT",
        "title": "writer_agent() drafts FinCo proposal (round_num = 1)",
        "desc": "Solutions consultant drafts 150-word scope for 6-week AI pilot within $35,000 cap.",
        "round_txt": "Round 1 / 2",
        "verdict_txt": "Verdict: pending",
        "active_nodes": {"writer"},
        "active_edge": "wc",
        "color": ACCENT,
    },
    {
        "badge": "ROUND 1 · REVISE",
        "title": "critic_agent() flags missing deliverable → REVISE",
        "desc": "Strict deal-desk reviewer checks 3-point rubric and returns actionable fixes.",
        "round_txt": "Round 1 / 2",
        "verdict_txt": "Verdict: REVISE",
        "active_nodes": {"critic"},
        "active_edge": "cw",
        "color": ERROR,
    },
    {
        "badge": "ROUND 2 · REVISE",
        "title": "writer_agent() incorporates critic feedback (round_num = 2)",
        "desc": "Adds weekly demos & security review deliverable while respecting the $35,000 budget.",
        "round_txt": "Round 2 / 2",
        "verdict_txt": "Verdict: re-checking...",
        "active_nodes": {"writer"},
        "active_edge": "wc",
        "color": AMBER,
    },
    {
        "badge": "ROUND 2 · PASS",
        "title": "critic_agent() verifies all 3 rubric checks → APPROVED",
        "desc": "Deliverables covered, budget respected, zero unsupported claims. Sets approved = True.",
        "round_txt": "Round 2 / 2",
        "verdict_txt": "Verdict: APPROVED",
        "active_nodes": {"critic"},
        "active_edge": "out",
        "color": SUCCESS,
    },
    {
        "badge": "APPROVED",
        "title": "Approved FinCo proposal exits cleanly to END",
        "desc": "Separating Writer and Critic personas catches gaps before the client sees the draft.",
        "round_txt": "Round 2 / 2",
        "verdict_txt": "Verdict: APPROVED",
        "active_nodes": {"out"},
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
    draw.text((s(32), s(22)), "Pattern 11: Review and Critique (Evaluator-Optimizer)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Writer Agent ↔ Deal-Desk Critic (MAX_ROUNDS = 2)  (11_review_and_critique/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "wc": ((278, 166), (402, 166)),
        "cw": ((402, 246), (278, 246)),
        "out": ((666, 206), (732, 206)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    draw_centered_text(draw, 340, 150, "draft", FONT_NODE_SUB, hi if active_edge == "wc" else MUTED)
    draw_centered_text(draw, 340, 264, "REVISE: feedback", FONT_NODE_SUB, hi if active_edge == "cw" else MUTED)
    draw_centered_text(draw, 699, 188, "APPROVED", FONT_SMALL_BOLD, hi if active_edge == "out" else MUTED)

    # Node 1: Writer Agent
    w_active = "writer" in active_nodes
    draw_rounded_box(draw, (32, 114, 274, 298), 12, CARD, hi if w_active else BORDER, width=3 if w_active else 2)
    draw_centered_text(draw, 153, 142, "Writer Agent", FONT_NODE, TEXT)
    draw_centered_text(draw, 153, 166, "writer_agent()", FONT_MONO, hi if w_active else ACCENT)
    draw_centered_text(draw, 153, 202, step["round_txt"], FONT_SMALL_BOLD, hi if w_active else TEXT)
    draw_centered_text(draw, 153, 238, "FinCo 6-wk AI pilot", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 153, 258, "Budget cap: $35,000", FONT_NODE_SUB, MUTED)

    # Node 2: Deal-Desk Critic
    c_active = "critic" in active_nodes
    draw_rounded_box(draw, (406, 114, 662, 298), 12, CARD, hi if c_active else BORDER, width=3 if c_active else 2)
    draw_centered_text(draw, 534, 142, "Deal-Desk Critic", FONT_NODE, TEXT)
    draw_centered_text(draw, 534, 166, "critic_agent()", FONT_MONO, hi if c_active else ACCENT)
    draw_centered_text(draw, 534, 200, "1. All deliverables?", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 534, 220, "2. Budget <= $35,000?", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 534, 240, "3. No unsupported claims?", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 534, 272, step["verdict_txt"], FONT_SMALL_BOLD, hi if c_active else ACCENT)

    # Node 3: Approved Output
    o_active = "out" in active_nodes
    draw_rounded_box(draw, (736, 156, 868, 256), 12, CARD, hi if o_active else BORDER, width=3 if o_active else 2)
    draw_centered_text(draw, 802, 194, "Approved", FONT_NODE, hi if o_active else TEXT)
    draw_centered_text(draw, 802, 220, "Send to FinCo", FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 348, W - 32, 448), 12, CARD, BORDER, width=1)
    draw_rounded_box(draw, (52, 368, 212, 396), 6, hi, hi, width=1)
    draw_centered_text(draw, 132, 382, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(228), s(371)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
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

    out_path = Path(__file__).resolve().parent / "11_review_and_critique.gif"
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
