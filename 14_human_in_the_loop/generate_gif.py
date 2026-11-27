"""Generate an animated GIF diagram for Pattern 14: Human-in-the-Loop (HITL).

Run with:
    uv run --offline --with pillow python 14_human_in_the_loop/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–13)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Safe draft)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (PAUSE checkpoint & Human gate)
SUCCESS = "#34D399"     # Emerald (Approved & Sent)
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
        "badge": "1. DRAFT",
        "title": "draft_outreach() writes personalized email for Maya Lin",
        "desc": "Runs safely with zero side effects and saves the 90-word draft to state['draft_email'].",
        "cp_status": "MemorySaver ready",
        "human_status": "Waiting for draft...",
        "send_status": "Blocked until approved",
        "active_nodes": {"draft"},
        "active_edges": {"e1"},
        "color": ACCENT,
    },
    {
        "badge": "2. PAUSED",
        "title": "Graph halts at interrupt_before=['send_email']",
        "desc": "MemorySaver checkpoints thread_id='outreach-demo-1' — nothing is sent without sign-off.",
        "cp_status": "PAUSED (state saved)",
        "human_status": "Inspects draft_email",
        "send_status": "Blocked until approved",
        "active_nodes": {"pause"},
        "active_edges": set(),
        "color": AMBER,
    },
    {
        "badge": "3. HUMAN GATE",
        "title": "Human approves & calls update_state(approved=True)",
        "desc": "Reviewer verifies tone and accuracy, then approves (or rejects to cancel delivery).",
        "cp_status": "approved = True",
        "human_status": "Approved [y]",
        "send_status": "Ready to resume",
        "active_nodes": {"human", "pause"},
        "active_edges": {"human", "e2"},
        "color": AMBER,
    },
    {
        "badge": "4. SENT",
        "title": "app.invoke(None) resumes → send_email() delivers",
        "desc": "Only after explicit human approval does send_email() execute the external action.",
        "cp_status": "Resumed",
        "human_status": "Approved [y]",
        "send_status": "SENT to Maya Lin",
        "active_nodes": {"send"},
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
    draw.text((s(32), s(22)), "Pattern 14: Human-in-the-Loop (HITL)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "interrupt_before Checkpoint + MemorySaver  (14_human_in_the_loop/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Dashed vertical checkpoint wall
    for y in range(86, 336, 14):
        draw.line([(s(450), s(y)), (s(450), s(min(y + 7, 336)))], fill=AMBER if step_idx in (1, 2) else BORDER, width=s(2))

    # Edges
    edges = {
        "e1": ((276, 158), (350, 158)),
        "e2": ((550, 158), (624, 158)),
        "human": ((450, 248), (450, 210)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name in active_edges
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node 1: draft_outreach
    d_active = "draft" in active_nodes
    draw_rounded_box(draw, (32, 102, 274, 214), 12, CARD, hi if d_active else BORDER, width=3 if d_active else 2)
    draw_centered_text(draw, 153, 128, "draft_outreach()", FONT_MONO, hi if d_active else TEXT)
    draw_centered_text(draw, 153, 154, "90-word cold email", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 153, 172, "for Maya Lin (NovaPay)", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 153, 196, "SAFE · READ-ONLY", FONT_SMALL_BOLD, ACCENT)

    # Node 2: Pause Checkpoint
    p_active = "pause" in active_nodes
    draw_rounded_box(draw, (354, 110, 546, 206), 12, CARD, hi if p_active else BORDER, width=3 if p_active else 2)
    draw_centered_text(draw, 450, 134, "CHECKPOINT", FONT_NODE, hi if p_active else TEXT)
    draw_centered_text(draw, 450, 158, "interrupt_before", FONT_MONO, AMBER)
    draw_centered_text(draw, 450, 184, step["cp_status"], FONT_NODE_SUB, hi if p_active else MUTED)

    # Node 3: Human Reviewer
    h_active = "human" in active_nodes
    draw_rounded_box(draw, (320, 250, 580, 324), 12, CARD, hi if h_active else BORDER, width=3 if h_active else 2)
    draw_centered_text(draw, 450, 276, "Human Reviewer", FONT_NODE, TEXT)
    draw_centered_text(draw, 450, 302, step["human_status"], FONT_NODE_SUB, hi if h_active else MUTED)

    # Node 4: send_email
    s_active = "send" in active_nodes
    draw_rounded_box(draw, (628, 102, 868, 214), 12, CARD, hi if s_active else BORDER, width=3 if s_active else 2)
    draw_centered_text(draw, 748, 128, "send_email()", FONT_MONO, hi if s_active else TEXT)
    draw_centered_text(draw, 748, 154, "External side effect", FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 748, 172, step["send_status"], FONT_NODE_SUB, hi if s_active else MUTED)
    draw_centered_text(draw, 748, 196, "IRREVERSIBLE ACTION", FONT_SMALL_BOLD, SUCCESS if s_active else AMBER)

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

    out_path = Path(__file__).resolve().parent / "14_human_in_the_loop.gif"
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
