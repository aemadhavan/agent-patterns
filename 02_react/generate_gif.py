"""Generate an animated GIF diagram for Pattern 02: ReAct (Reason + Act).

Run with:
    uv run --with pillow python 02_react/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Render at 2x for crisp anti-aliasing, then downsample
SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01_single_agent.gif)
BG = "#0F172A"
CARD = "#1E293B"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Highlight for Cycle 2 / loop-back
SUCCESS = "#34D399"     # Emerald for Final Answer
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
    head_len = s(10)
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
        "badge": "INPUT",
        "cycle": "START",
        "title": "Customer asks about delayed order ORD-4821",
        "desc": '"Where is my order ORD-4821? It was supposed to arrive two days ago."',
        "thought": "Plan next step",
        "action": "call tool()",
        "obs": "Tool output feeds back",
        "active_nodes": {"user"},
        "active_edge": "in",
        "color": ACCENT,
    },
    {
        "badge": "CYCLE 1 · THOUGHT",
        "cycle": "CYCLE 1",
        "title": "Reason: Check order status first",
        "desc": "No tracking ID yet — the agent decides to inspect ORD-4821 before doing anything else.",
        "thought": "Check ORD-4821 status",
        "action": "call tool()",
        "obs": "Tool output feeds back",
        "active_nodes": {"thought"},
        "active_edge": "ta",
        "color": ACCENT,
    },
    {
        "badge": "CYCLE 1 · ACTION",
        "cycle": "CYCLE 1",
        "title": "Act: get_order_status('ORD-4821')",
        "desc": "Calls the order-status tool to retrieve shipment state and carrier tracking ID.",
        "thought": "Check ORD-4821 status",
        "action": "get_order_status()",
        "obs": "Tool output feeds back",
        "active_nodes": {"action"},
        "active_edge": "ao",
        "color": ACCENT,
    },
    {
        "badge": "CYCLE 1 · OBSERVE",
        "cycle": "CYCLE 1",
        "title": "Observe: Status is DELAYED + tracking ID found",
        "desc": "New observation feeds back into Thought — triggering a second ReAct cycle.",
        "thought": "Check ORD-4821 status",
        "action": "get_order_status()",
        "obs": "DELAYED · Tracking ID found",
        "active_nodes": {"obs"},
        "active_edge": "ot",
        "color": AMBER,
    },
    {
        "badge": "CYCLE 2 · ACT",
        "cycle": "CYCLE 2",
        "title": "Adapt: Call get_carrier_update(tracking_id)",
        "desc": "Using Cycle 1's tracking ID, the agent fetches the live carrier depot scan.",
        "thought": "Fetch live carrier ETA",
        "action": "get_carrier_update()",
        "obs": "DELAYED · Tracking ID found",
        "active_nodes": {"thought", "action"},
        "active_edge": "ta",
        "color": AMBER,
    },
    {
        "badge": "CYCLE 2 · OBSERVE",
        "cycle": "CYCLE 2",
        "title": "Observe: Live depot delay & revised ETA returned",
        "desc": "Observation feeds back to Thought: we now have the exact reason and new ETA.",
        "thought": "Fetch live carrier ETA",
        "action": "get_carrier_update()",
        "obs": "Depot delay · New ETA ready",
        "active_nodes": {"obs"},
        "active_edge": "ot",
        "color": AMBER,
    },
    {
        "badge": "FINAL ANSWER",
        "cycle": "DONE",
        "title": "Goal reached → Exit loop & reply with new ETA",
        "desc": "The agent stops calling tools and sends a helpful, accurate reply to the customer.",
        "thought": "Goal met → Reply!",
        "action": "Stop loop",
        "obs": "Depot delay · New ETA ready",
        "active_nodes": {"thought", "user"},
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
    draw.text((s(32), s(22)), "Pattern 02: ReAct (Reason + Act)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Thought → Action → Observation Loop  (02_react/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 24 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 16), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "in": ((202, 188), (294, 152)),
        "out": ((294, 174), (202, 212)),
        "ta": ((522, 146), (620, 146)),
        "ao": ((714, 188), (642, 248)),
        "ot": ((442, 248), (392, 188)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Center Cycle label
    draw_centered_text(draw, 542, 214, step["cycle"], FONT_SMALL_BOLD, hi)

    # Node: User
    u_active = "user" in active_nodes
    draw_rounded_box(draw, (32, 156, 198, 250), 12, CARD, hi if u_active else BORDER, width=3 if u_active else 2)
    draw_centered_text(draw, 115, 184, "User", FONT_NODE, TEXT)
    draw_centered_text(draw, 115, 210, '"Where is order', FONT_NODE_SUB, MUTED)
    draw_centered_text(draw, 115, 228, 'ORD-4821?"', FONT_NODE_SUB, MUTED)

    # Node: 1. Thought
    t_active = "thought" in active_nodes
    draw_rounded_box(draw, (298, 108, 518, 184), 12, CARD, hi if t_active else BORDER, width=3 if t_active else 2)
    draw_centered_text(draw, 408, 134, "1. Thought", FONT_NODE, TEXT)
    draw_centered_text(draw, 408, 160, step["thought"], FONT_NODE_SUB, hi if t_active else MUTED)

    # Node: 2. Action
    a_active = "action" in active_nodes
    draw_rounded_box(draw, (624, 108, 868, 184), 12, CARD, hi if a_active else BORDER, width=3 if a_active else 2)
    draw_centered_text(draw, 746, 134, "2. Action", FONT_NODE, TEXT)
    draw_centered_text(draw, 746, 160, step["action"], FONT_MONO, hi if a_active else MUTED)

    # Node: 3. Observation
    o_active = "obs" in active_nodes
    draw_rounded_box(draw, (424, 248, 680, 320), 12, CARD, hi if o_active else BORDER, width=3 if o_active else 2)
    draw_centered_text(draw, 552, 274, "3. Observation", FONT_NODE, TEXT)
    draw_centered_text(draw, 552, 298, step["obs"], FONT_NODE_SUB, hi if o_active else MUTED)

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
        for t in [0.15, 0.35, 0.55, 0.75, 0.90]:
            frames.append(render_frame(idx, dot_t=t))
            durations.append(140)
        frames.append(render_frame(idx, dot_t=None))
        durations.append(1350)

    out_path = Path(__file__).resolve().parent / "02_react.gif"
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
