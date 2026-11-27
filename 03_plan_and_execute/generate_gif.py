"""Generate an animated GIF diagram for Pattern 03: Plan-and-Execute.

Run with:
    uv run --with pillow python 03_plan_and_execute/generate_gif.py
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 900, 480
CW, CH = W * SCALE, H * SCALE

# Modern dark-slate palette (matches 01 & 02)
BG = "#0F172A"
CARD = "#1E293B"
INNER = "#0F172A"
BORDER = "#334155"
ACCENT = "#38BDF8"      # Sky blue (Planner)
ACCENT_SOFT = "#0284C7"
AMBER = "#FBBF24"       # Amber (Executor running steps)
SUCCESS = "#34D399"     # Emerald (Completed / Synthesizer)
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
FONT_NODE = load_font(15, bold=True)
FONT_NODE_SUB = load_font(11, bold=False)
FONT_CHK = load_font(12, bold=False)
FONT_CHK_BOLD = load_font(12, bold=True)
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


CHECKLIST = [
    "1. Identify competitors",
    "2. Gather pricing tiers",
    "3. Compare features",
    "4. Summarize key risks",
]

STEPS = [
    {
        "badge": "1. PLANNER",
        "title": "Planner creates an explicit 4-step roadmap up front",
        "desc": "Separates strategy from execution: turns the briefing prompt into 4 ordered steps.",
        "active_node": "planner",
        "active_edge": "pe",
        "done_count": 0,
        "active_chk": -1,
        "color": ACCENT,
    },
    {
        "badge": "2. EXEC 1 / 4",
        "title": "Executor runs Step 1: Identify competitors",
        "desc": "Researches top B2B AI observability rivals and stores 3–4 bullets in step_outputs[0].",
        "active_node": "executor",
        "active_edge": None,
        "done_count": 0,
        "active_chk": 0,
        "color": AMBER,
    },
    {
        "badge": "3. EXEC 2 / 4",
        "title": "Executor runs Step 2: Gather pricing tiers",
        "desc": "Uses Step 1 as prior context to map enterprise pricing models.",
        "active_node": "executor",
        "active_edge": None,
        "done_count": 1,
        "active_chk": 1,
        "color": AMBER,
    },
    {
        "badge": "4. EXEC 3 / 4",
        "title": "Executor runs Step 3: Compare features",
        "desc": "Carries rolling context (outputs[-2:]) to compare enterprise capabilities.",
        "active_node": "executor",
        "active_edge": None,
        "done_count": 2,
        "active_chk": 2,
        "color": AMBER,
    },
    {
        "badge": "5. EXEC 4 / 4",
        "title": "Executor runs Step 4: Summarize key risks",
        "desc": "Finishes the checklist and passes all 4 step_outputs to the Synthesizer.",
        "active_node": "executor",
        "active_edge": "es",
        "done_count": 3,
        "active_chk": 3,
        "color": AMBER,
    },
    {
        "badge": "6. SYNTHESIZE",
        "title": "Synthesizer compiles the Executive Briefing",
        "desc": "Merges all 4 executed sections into one crisp, executive-ready final report.",
        "active_node": "synth",
        "active_edge": None,
        "done_count": 4,
        "active_chk": -1,
        "color": SUCCESS,
    },
]


def render_frame(step_idx: int, dot_t: float | None) -> Image.Image:
    step = STEPS[step_idx]
    active_node = step["active_node"]
    active_edge = step["active_edge"]
    hi = step["color"]

    img = Image.new("RGB", (CW, CH), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((s(32), s(22)), "Pattern 03: Plan-and-Execute", font=FONT_TITLE, fill=TEXT)
    draw.text((s(32), s(48)), "Planner → Executor (4-Step Checklist) → Synthesizer  (03_plan_and_execute/app.py)", font=FONT_SUB, fill=MUTED)
    draw.line([(s(32), s(74)), (s(W - 32), s(74))], fill=BORDER, width=s(1))

    # Step progress pills
    for i in range(len(STEPS)):
        px = W - 32 - (len(STEPS) - i) * 26 + 6
        py = 36
        fill = hi if i == step_idx else (ACCENT_SOFT if i < step_idx else BORDER)
        draw.rounded_rectangle([s(px), s(py), s(px + 18), s(py + 6)], radius=s(3), fill=fill)

    # Edges
    edges = {
        "pe": ((248, 206), (306, 206)),
        "es": ((602, 206), (660, 206)),
    }
    for name, (p1, p2) in edges.items():
        is_active = name == active_edge
        color = hi if is_active else BORDER
        draw_arrow(draw, p1, p2, color=color, width=3 if is_active else 2, dot_t=dot_t if is_active else None)

    # Node 1: Planner
    p_active = active_node == "planner"
    draw_rounded_box(draw, (32, 120, 244, 294), 12, CARD, hi if p_active else BORDER, width=3 if p_active else 2)
    draw_centered_text(draw, 138, 148, "1. Planner", FONT_NODE, TEXT)
    draw_centered_text(draw, 138, 170, "planner_node", FONT_NODE_SUB, MUTED)
    draw_rounded_box(draw, (48, 190, 228, 276), 8, INNER, hi if p_active else BORDER, width=1)
    draw_centered_text(draw, 138, 210, "UPFRONT STRATEGY", FONT_SMALL_BOLD, ACCENT)
    draw_centered_text(draw, 138, 234, "Drafts 4 numbered", FONT_NODE_SUB, TEXT if p_active else MUTED)
    draw_centered_text(draw, 138, 254, "steps before acting", FONT_NODE_SUB, TEXT if p_active else MUTED)

    # Node 2: Executor (4-step checklist)
    e_active = active_node == "executor"
    draw_rounded_box(draw, (310, 96, 598, 318), 12, CARD, hi if e_active else BORDER, width=3 if e_active else 2)
    draw_centered_text(draw, 454, 122, "2. Executor", FONT_NODE, TEXT)
    draw_centered_text(draw, 454, 142, "Runs plan[0..3] with rolling context", FONT_NODE_SUB, MUTED)

    for i, label in enumerate(CHECKLIST):
        y1 = 160 + i * 36
        y2 = y1 + 28
        if i < step["done_count"]:
            prefix, color, font = "[✓] ", SUCCESS, FONT_CHK_BOLD
            outline = SUCCESS
        elif i == step["active_chk"]:
            prefix, color, font = "[▶] ", AMBER, FONT_CHK_BOLD
            outline = AMBER
        else:
            prefix, color, font = "[ ] ", MUTED, FONT_CHK
            outline = BORDER
        draw_rounded_box(draw, (330, y1, 578, y2), 6, INNER, outline, width=1)
        draw.text((s(344), s(y1 + 6)), f"{prefix}{label}", font=font, fill=color)

    # Node 3: Synthesizer
    s_active = active_node == "synth"
    draw_rounded_box(draw, (664, 120, 868, 294), 12, CARD, hi if s_active else BORDER, width=3 if s_active else 2)
    draw_centered_text(draw, 766, 148, "3. Synthesizer", FONT_NODE, TEXT)
    draw_centered_text(draw, 766, 170, "synthesizer_node", FONT_NODE_SUB, MUTED)
    draw_rounded_box(draw, (680, 190, 852, 276), 8, INNER, hi if s_active else BORDER, width=1)
    draw_centered_text(draw, 766, 210, "FINAL OUTPUT", FONT_SMALL_BOLD, SUCCESS)
    draw_centered_text(draw, 766, 234, "Crisp Executive", FONT_NODE_SUB, TEXT if s_active else MUTED)
    draw_centered_text(draw, 766, 254, "Briefing Report", FONT_NODE_SUB, TEXT if s_active else MUTED)

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
            for t in [0.15, 0.35, 0.55, 0.75, 0.90]:
                frames.append(render_frame(idx, dot_t=t))
                durations.append(140)
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1250)
        else:
            frames.append(render_frame(idx, dot_t=None))
            durations.append(1400)

    out_path = Path(__file__).resolve().parent / "03_plan_and_execute.gif"
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
