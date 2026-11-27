"""Generate a 1920x1080 LinkedIn article cover banner featuring all 15 agent miniatures.

Run with:
    uv run --offline --with pillow python generate_banner.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1920, 1080

# Matching dark-slate palette
BG = "#0B1120"
HEADER_BG = "#0F172A"
CARD = "#162032"
BORDER = "#334155"
ACCENT = "#38BDF8"
AMBER = "#FBBF24"
SUCCESS = "#34D399"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BADGE_TEXT = "#082F49"

PATTERNS = [
    ("01", "01_single_agent", "Single-Agent", 0, ACCENT),
    ("02", "02_react", "ReAct Loop", 2, ACCENT),
    ("03", "03_plan_and_execute", "Plan & Execute", 0, ACCENT),
    ("04", "04_sequential", "Sequential", 0, ACCENT),
    ("05", "05_parallel", "Parallel", 0, ACCENT),
    ("06", "06_loop", "Bounded Loop", 0, AMBER),
    ("07", "07_routing", "Routing", 2, AMBER),
    ("08", "08_coordinator", "Coordinator", 0, AMBER),
    ("09", "09_hierarchical", "Hierarchical", 0, AMBER),
    ("10", "10_swarm", "Swarm", 0, AMBER),
    ("11", "11_review_and_critique", "Review & Critique", 0, SUCCESS),
    ("12", "12_iterative_refinement", "Reflection", 0, SUCCESS),
    ("13", "13_tool_use_and_rag", "Tool Use & RAG", 0, SUCCESS),
    ("14", "14_human_in_the_loop", "Human-in-the-Loop", 0, SUCCESS),
    ("15", "15_elephant_goldfish", "Elephant-Goldfish", 0, SUCCESS),
]


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
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


FONT_HERO = load_font(54, bold=True)
FONT_SUB = load_font(22, bold=False)
FONT_PILL = load_font(16, bold=True)
FONT_CARD_NUM = load_font(15, bold=True, mono=True)
FONT_CARD_TITLE = load_font(18, bold=True)


def extract_diagram_crop(gif_path: Path, frame_idx: int) -> Image.Image:
    """Extract the pure diagram region (y=76..342) from a 900x480 pattern GIF."""
    with Image.open(gif_path) as im:
        n_frames = getattr(im, "n_frames", 1)
        im.seek(min(frame_idx, n_frames - 1))
        rgb = im.convert("RGB")
        # Crop out the top header and bottom caption bar so the miniature is pure diagram
        return rgb.crop((16, 76, 884, 342))


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle top header bar
    draw.rectangle([0, 0, W, 198], fill=HEADER_BG)
    draw.line([(0, 198), (W, 198)], fill=BORDER, width=2)

    # Hero title & subtitle
    draw.text((56, 34), "15 AI Agent Design Patterns", font=FONT_HERO, fill=TEXT)
    draw.text(
        (58, 108),
        "Visual Blueprints for Reliable AI Agents  ·  Runnable LangGraph + Claude Playbook",
        font=FONT_SUB,
        fill=MUTED,
    )

    # Right-side tech pills
    pills = [
        ("LangGraph", ACCENT),
        ("Claude", AMBER),
        ("Arize Phoenix", SUCCESS),
    ]
    px = W - 56
    for label, color in reversed(pills):
        bbox = draw.textbbox((0, 0), label, font=FONT_PILL)
        pw = (bbox[2] - bbox[0]) + 32
        px -= pw
        draw.rounded_rectangle([px, 52, px + pw, 88], radius=18, fill=CARD, outline=color, width=2)
        draw.text((px + 16, 60), label, font=FONT_PILL, fill=color)
        px -= 14

    # Repo URL under pills
    repo_txt = "github.com/aemadhavan/agent-patterns"
    rb = draw.textbbox((0, 0), repo_txt, font=FONT_PILL)
    draw.text((W - 56 - (rb[2] - rb[0]), 112), repo_txt, font=FONT_PILL, fill=MUTED)

    # 5 columns x 3 rows grid of miniatures
    cols, rows = 5, 3
    margin_x = 48
    margin_top = 224
    gap_x = 22
    gap_y = 22
    card_w = (W - 2 * margin_x - (cols - 1) * gap_x) // cols
    card_h = (H - margin_top - 40 - (rows - 1) * gap_y) // rows

    for idx, (num, folder, title, frame_idx, accent) in enumerate(PATTERNS):
        r = idx // cols
        c = idx % cols
        x1 = margin_x + c * (card_w + gap_x)
        y1 = margin_top + r * (card_h + gap_y)
        x2 = x1 + card_w
        y2 = y1 + card_h

        # Card container
        draw.rounded_rectangle([x1, y1, x2, y2], radius=14, fill=CARD, outline=BORDER, width=2)

        # Miniature diagram area
        gif_path = ROOT / folder / f"{folder}.gif"
        crop = extract_diagram_crop(gif_path, frame_idx)
        pad = 10
        avail_w = card_w - 2 * pad
        avail_h = card_h - 52
        # Fit preserving aspect ratio
        scale = min(avail_w / crop.width, avail_h / crop.height)
        nw, nh = int(crop.width * scale), int(crop.height * scale)
        thumb = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        tx = x1 + (card_w - nw) // 2
        ty = y1 + pad + (avail_h - nh) // 2
        img.paste(thumb, (tx, ty))

        # Card footer bar
        fy = y2 - 42
        draw.line([(x1 + 10, fy), (x2 - 10, fy)], fill=BORDER, width=1)
        # Number badge
        draw.rounded_rectangle([x1 + 12, fy + 8, x1 + 48, fy + 33], radius=6, fill=accent)
        nb = draw.textbbox((0, 0), num, font=FONT_CARD_NUM)
        draw.text((x1 + 30 - (nb[2] - nb[0]) // 2, fy + 12), num, font=FONT_CARD_NUM, fill=BADGE_TEXT)
        # Pattern title
        draw.text((x1 + 58, fy + 10), title, font=FONT_CARD_TITLE, fill=TEXT)

    out_path = ROOT / "linkedin_banner.jpg"
    img.save(out_path, format="JPEG", quality=95, subsampling=0)
    print(f"Saved {out_path} ({W}x{H}, {out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
