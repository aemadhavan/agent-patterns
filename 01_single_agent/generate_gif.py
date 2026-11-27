"""Generate an animated GIF diagram for Pattern 01: Single-Agent System.

Run with:
    uv run --with pillow python 01_single_agent/generate_gif.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Canvas settings (render at 2x for crisp anti-aliasing, then downsample)
SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (great contrast on GitHub, LinkedIn, and slides)
BG = "#0F172A"
CARD = "#1E293B"
CARD_ACTIVE = "#1E293B"
INNER_BOX = "#0F172A"
BORDER = "#334155"
BORDER_ACTIVE = "#38BDF8"
ACCENT = "#38BDF8"       # Sky blue
ACCENT_SOFT = "#0284C7"
SUCCESS = "#34D399"      # Emerald
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BADGE_BG = "#0EA5E9"
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
FONT_NODE = load_font(15, bold=True)
FONT_NODE_SUB = load_font(12, bold=False)
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

    # Arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    head_len = s(10)
    head_ang = math.pi / 6
    ax1 = x2 - head_len * math.cos(angle - head_ang)
    ay1 = y2 - head_len * math.sin(angle - head_ang)
    ax2 = x2 - head_len * math.cos(angle + head_ang)
    ay2 = y2 - head_len * math.sin(angle + head_ang)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)

    # Animated traveling dot
    if dot_t is not None:
        dx = x1 + (x2 - x1) * dot_t
        dy = y1 + (y2 - y1) * dot_t
        r = s(5)
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=TEXT, outline=color, width=s(2))


STEPS = [
    {
        "badge": "STEP 1 / 5",
        "title": "User submits a request",
        "desc": '"My GlobalProtect VPN keeps failing with error 403 even after clearing cache."',
        "active_nodes": {"user"},
        "active_edge": "user_to_agent",
    },
    {
        "badge": "STEP 2 / 5",
        "title": "Single Agent reasons with its System Prompt",
        "desc": "One LLM owns the full task. Policy says: check IT knowledge base before escalating.",
        "active_nodes": {"agent"},
        "active_edge": None,
    },
    {
        "badge": "STEP 3 / 5",
        "title": "Agent calls Tool 1: search_it_kb()",
        "desc": 'Queries the IT KB for "GlobalProtect VPN 403" and reads back troubleshooting steps.',
        "active_nodes": {"agent", "kb"},
        "active_edge": "agent_to_kb",
    },
    {
        "badge": "STEP 4 / 5",
        "title": "Unresolved 403 → Agent calls Tool 2: create_it_ticket()",
        "desc": "Since cache was already cleared, the agent escalates by opening an IT support ticket.",
        "active_nodes": {"agent", "ticket"},
        "active_edge": "agent_to_ticket",
    },
    {
        "badge": "STEP 5 / 5",
        "title": "Agent returns one unified answer",
        "desc": "Combines KB guidance + new ticket ID into a single reply. No multi-agent handoffs needed.",
        "active_nodes": {"agent", "user"},
        "active_edge": "agent_to_user",
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    active_nodes = step["active_nodes"]
    active_edge = step["active_edge"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 01: Single-Agent System", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "One LLM  ·  One System Prompt  ·  Two Tools  (01_single_agent/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills (top right)
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = ACCENT if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "user_to_agent": ((210, 198), (312, 198)),
        "agent_to_user": ((312, 226), (210, 226)),
        "agent_to_kb": ((568, 186), (656, 152)),
        "agent_to_ticket": ((568, 240), (656, 274)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = SUCCESS if (is_active and name == "agent_to_user") else (ACCENT if is_active else BORDER)
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node: User
    u_active = "user" in active_nodes
    u_border = SUCCESS if (step_idx == 4) else (BORDER_ACTIVE if u_active else BORDER)
    draw_rounded_box(draw, (32, 162, 208, 262), 12, CARD, u_border, width=3 if u_active else 2)
    draw_centered_text(draw, 120, 192, "User", FONT_NODE, TEXT)
    draw_centered_text(draw, 120, 218, '"VPN error 403', FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 120, 236, 'after cache clear"', FONT_NODE_SUB, MUTED)

    # Node: Single Agent (Hub)
    a_active = "agent" in active_nodes
    draw_rounded_box(draw, (316, 118, 564, 306), 14, CARD, BORDER_ACTIVE if a_active else BORDER, width=3 if a_active else 2)
    draw_centered_text(draw, 440, 145, "Single Agent (LLM)", FONT_NODE, TEXT)
    draw_centered_text(draw, 440, 167, "1 Model  ·  1 Loop", FONT_NODE_SUB, MUTED)
    # System prompt inner box
    draw_rounded_box(draw, (336, 186, 544, 288), 10, INNER_BOX, ACCENT if a_active else BORDER, width=1)
    draw_centered_text(draw, 440, 205, "SYSTEM PROMPT", FONT_SMALL_BOLD, ACCENT)
    draw_centered_text(draw, 440, 228, "1. Search IT KB first", FONT_NODE_SUB, TEXT if a_active else MUTED)
    draw_centered_text(draw, 440, 248, "2. If HTTP 403 persists →", FONT_NODE_SUB, TEXT if a_active else MUTED)
    draw_centered_text(draw, 440, 268, "raise an IT ticket", FONT_NODE_SUB, TEXT if a_active else MUTED)

    # Node: Tool 1 (search_it_kb)
    kb_active = "kb" in active_nodes
    draw_rounded_box(draw, (660, 112, 868, 194), 12, CARD, BORDER_ACTIVE if kb_active else BORDER, width=3 if kb_active else 2)
    draw_centered_text(draw, 764, 142, "search_it_kb()", FONT_MONO, ACCENT if kb_active else TEXT)
    draw_centered_text(draw, 764, 168, "Read-only KB lookup", FONT_NODE_SUB, MUTED)

    # Node: Tool 2 (create_it_ticket)
    tk_active = "ticket" in active_nodes
    draw_rounded_box(draw, (660, 230, 868, 312), 12, CARD, BORDER_ACTIVE if tk_active else BORDER, width=3 if tk_active else 2)
    draw_centered_text(draw, 764, 260, "create_it_ticket()", FONT_MONO, ACCENT if tk_active else TEXT)
    draw_centered_text(draw, 764, 286, "Action / Escalation", FONT_NODE_SUB, MUTED)

    # Footer explanation box
    draw_rounded_box(draw, (32, 344, W - 32, 448), 12, CARD, BORDER, width=1)
    badge_color = SUCCESS if step_idx == 4 else BADGE_BG
    draw_rounded_box(draw, (52, 366, 152, 394), 6, badge_color, badge_color, width=1)
    draw_centered_text(draw, 102, 380, step["badge"], FONT_SMALL_BOLD, BADGE_TEXT)
    draw.text((s(168), s(369)), step["title"], font=FONT_STEP_TITLE, fill=TEXT)
    draw.text((s(52), s(408)), step["desc"], font=FONT_STEP_DESC, fill=MUTED)

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    frames: list[Image.Image] = []
    durations: list[int] = []

    for idx, step in enumerate(STEPS):
        if step["active_edge"]:
            # Animate packet traveling along edge (6 frames) + hold (1 frame)
            for t in [0.15, 0.32, 0.50, 0.68, 0.85]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(140)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1300)
        else:
            # Static reasoning step
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1700)

    out_path = Path(__file__).resolve().parent / "01_single_agent.gif"
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
