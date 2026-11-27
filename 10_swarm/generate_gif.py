"""Generate an animated GIF diagram for Pattern 10: Swarm (Peer-to-Peer Handoffs).

Run with:
    uv run --offline --with pillow python 10_swarm/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01–09)
BG = "#0F172A"
CARD = "#1E293B"
INNER = "#0F172A"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Mid-incident handoffs)
SUCCESS = "#34D399"     # Emerald (Resolved)
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
        "badge": "HOP 1 · DETECT",
        "title": "Detection confirms P1 Checkout 504 → HANDOFF: diagnostics",
        "desc": "Logs severity & blast radius to shared_log and hands off directly to Diagnostics.",
        "log_txt": "Entries: 1 · [Detection]",
        "active_nodes": {1},
        "done_nodes": set(),
        "active_edge": "e12",
        "color": ACCENT,
    },
    {
        "badge": "HOP 2 · DIAGNOSE",
        "title": "Diagnostics isolates deploy v4.12.3 → HANDOFF: remediation",
        "desc": "Reads shared_log, identifies root cause, and passes the baton to Remediation.",
        "log_txt": "Entries: 2 · [+Diagnostics]",
        "active_nodes": {2},
        "done_nodes": {1},
        "active_edge": "e23",
        "color": AMBER,
    },
    {
        "badge": "HOP 3 · REMEDIATE",
        "title": "Remediation proposes rollback → HANDOFF: communications",
        "desc": "Appends rollback/mitigation steps to shared_log and hands off to Communications.",
        "log_txt": "Entries: 3 · [+Remediation]",
        "active_nodes": {3},
        "done_nodes": {1, 2},
        "active_edge": "e34",
        "color": AMBER,
    },
    {
        "badge": "HOP 4 · COMMS",
        "title": "Communications drafts status-page update → HANDOFF: done",
        "desc": "Reads the full shared_log, writes customer update, and signals HANDOFF: done.",
        "log_txt": "Entries: 4 · [+Comms]",
        "active_nodes": {4},
        "done_nodes": {1, 2, 3},
        "active_edge": None,
        "color": SUCCESS,
    },
    {
        "badge": "RESOLVED",
        "title": "Swarm exits cleanly (hops = 4 < 5) with full incident log",
        "desc": "Peers collaborated autonomously over shared_log — zero central manager bottleneck.",
        "log_txt": "Entries: 4 · Complete",
        "active_nodes": set(),
        "done_nodes": {1, 2, 3, 4},
        "active_edge": None,
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 10: Swarm (Multi-Agent Collaboration)", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Peer-to-Peer Handoffs over Shared Incident Log  (10_swarm/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Handoff Edges (clockwise)
    edges = {
        "e12": ((268, 126), (626, 126)),
        "e23": ((746, 162), (746, 250)),
        "e34": ((626, 286), (268, 286)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == step["active_edge"]
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Center: Shared Incident Log
    draw_rounded_box(draw, (318, 174, 582, 240), 10, INNER, hi if step_idx < 4 else SUCCESS, width=2)
    draw_centered_text(draw, 450, 196, "SHARED INCIDENT LOG", FONT_SMALL_BOLD, hi if step_idx < 4 else SUCCESS)
    draw_centered_text(draw, 450, 220, step["log_txt"], FONT_NODE_SUB, MUTED)

    # 4 Peer Nodes
    peers = [
        (1, (32, 92, 264, 160), "1. Detection", "Severity & blast radius"),
        (2, (630, 92, 868, 160), "2. Diagnostics", "Root cause (v4.12.3)"),
        (3, (630, 252, 868, 320), "3. Remediation", "Mitigation & rollback"),
        (4, (32, 252, 264, 320), "4. Communications", "Status-page update"),
    ]
    for num, box, title, sub in peers:
        x1, y1, x2, y2 = box
        cx = (x1 + x2) / 2
        is_active = num in step["active_nodes"]
        is_done = num in step["done_nodes"]
        outline = hi if is_active else (SUCCESS if is_done else BORDER)
        draw_rounded_box(draw, box, 12, CARD, outline, width=3 if is_active else 2)
        draw_centered_text(draw, cx, y1 + 24, title, FONT_NODE, hi if is_active else TEXT)
        draw_centered_text(draw, cx, y1 + 48, sub, FONT_NODE_SUB, MUTED)

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

    out_path = Path(__file__).resolve().parent / "10_swarm.gif"
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
