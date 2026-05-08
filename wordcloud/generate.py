"""
wordcloud/generate.py
Reads words from wordcloud/words.txt, generates a new PNG, updates metadata.json.
Triggered by GitHub Actions on issue events.
"""

import os
import json
import random
import re
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt

WORDS_FILE   = Path("wordcloud/words.txt")
OUTPUT_IMAGE = Path("wordcloud/wordcloud.png")
METADATA     = Path("wordcloud/metadata.json")

# ── Colour palette matching profile theme ──────────────────────────────────────
COLORS = ["#86A8E7", "#7F7FD5", "#91EAE4", "#b8c6fb", "#d4e0ff", "#ffffff"]

def random_color(*args, **kwargs):
    return random.choice(COLORS)

# ── Load or create files ───────────────────────────────────────────────────────
WORDS_FILE.parent.mkdir(exist_ok=True)

if not WORDS_FILE.exists():
    WORDS_FILE.write_text("")

if not METADATA.exists():
    METADATA.write_text(json.dumps({
        "total_words": 0,
        "clouds_created": 0,
        "participants": 0
    }))

meta = json.loads(METADATA.read_text())
words = [w.strip() for w in WORDS_FILE.read_text().splitlines() if w.strip()]

# ── Parse incoming issue ───────────────────────────────────────────────────────
issue_title = os.environ.get("ISSUE_TITLE", "")

if issue_title.startswith("wordcloud|add|"):
    new_word = re.sub(r"wordcloud\|add\|", "", issue_title).strip()
    # Basic sanity: letters/numbers only, max 30 chars
    new_word = re.sub(r"[^a-zA-Z0-9\+\#\.]", "", new_word)[:30]
    if new_word:
        words.append(new_word)
        WORDS_FILE.write_text("\n".join(words))
        meta["total_words"] = len(words)
        meta["participants"] = meta.get("participants", 0) + 1

elif issue_title.startswith("wordcloud|shuffle"):
    pass  # just regenerate with existing words

# ── Generate word cloud ────────────────────────────────────────────────────────
if words:
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    wc = WordCloud(
        width=1200,
        height=600,
        background_color=None,
        mode="RGBA",
        color_func=random_color,
        max_words=200,
        prefer_horizontal=0.7,
        random_state=random.randint(0, 9999),
        font_path=None,          # uses system default
        collocations=False,
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.patch.set_alpha(0)
    plt.tight_layout(pad=0)
    plt.savefig(OUTPUT_IMAGE, dpi=150, bbox_inches="tight",
                transparent=True, format="png")
    plt.close()

meta["clouds_created"] = meta.get("clouds_created", 0) + 1
METADATA.write_text(json.dumps(meta, indent=2))

print(f"✅ Word cloud generated. Words: {len(words)}, Clouds: {meta['clouds_created']}")
