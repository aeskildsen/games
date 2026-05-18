#!/usr/bin/env python3
"""Generate a delightfully unhinged index.html for the vibe-coded games."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import hashlib
import json


class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = None
        self.description = None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            a = dict(attrs)
            if a.get("name") == "description" and a.get("content"):
                self.description = a["content"].strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.title is None:
            text = data.strip()
            if text:
                self.title = text


def extract(path: Path):
    parser = MetaExtractor()
    try:
        parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        pass
    return parser.title or path.stem, parser.description


EMOJIS = [
    "🎮", "🕹️", "👾", "🦑", "🐸", "🧀", "🐭", "🍕", "🔥", "✨",
    "🌶️", "🦖", "🛸", "🪩", "🧠", "🎲", "🎯", "🐙", "🍌", "🦄",
    "💀", "👻", "🤖", "🐉", "🌈", "⚡", "💥", "🪐", "🧨", "🥨",
]

TAGLINES = [
    "100% vibes, 0% planning",
    "Compiled by feel, debugged by hope",
    "Powered by snacks and confusion",
    "Each game is a single .html file. Don't ask.",
    "If it doesn't work, refresh until it does",
    "Engineered with reckless optimism",
    "Code first, regret later",
    "Untested by professionals",
    "All bugs are intentional features",
    "Free range, gluten-free, vibe-fed",
]


def card_for(path: Path) -> dict:
    title, desc = extract(path)
    h = int(hashlib.sha256(path.name.encode()).hexdigest(), 16)
    return {
        "href": path.name,
        "title": title,
        "desc": desc or "",
        "emoji": EMOJIS[h % len(EMOJIS)],
        "hue": (h // 7) % 360,
    }


BACK_BUTTON_MARKER = "<!-- games:back-button -->"
BACK_BUTTON_SNIPPET = """<!-- games:back-button -->
<a href="index.html" id="games-home-btn" aria-label="Back to games index"><span aria-hidden="true">←</span> Home</a>
<style>
  #games-home-btn {
    position: fixed; top: 1rem; left: 1rem; z-index: 99999;
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.5rem 0.95rem; border-radius: 999px;
    background: rgba(0,0,0,0.55); color: #fff;
    font: 700 0.9rem/1 ui-rounded, "SF Pro Rounded", system-ui, sans-serif;
    text-decoration: none; border: 1px solid rgba(255,255,255,0.25);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    transition: transform .2s cubic-bezier(.2,.9,.3,1.4), background .2s, box-shadow .2s;
  }
  #games-home-btn:hover {
    transform: translateX(-4px) scale(1.05);
    background: linear-gradient(135deg, #ff006e, #8338ec);
    box-shadow: 0 8px 24px rgba(255,0,110,.45);
  }
  #games-home-btn span { font-size: 1.15rem; line-height: 1; }
</style>
"""


def ensure_back_button(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if BACK_BUTTON_MARKER in text:
        return False
    if "</body>" in text:
        new = text.replace("</body>", BACK_BUTTON_SNIPPET + "</body>", 1)
    else:
        new = text + "\n" + BACK_BUTTON_SNIPPET
    path.write_text(new, encoding="utf-8")
    return True


root = Path(".")
pages = sorted(p for p in root.glob("*.html") if p.name != "index.html")

injected = [p.name for p in pages if ensure_back_button(p)]
if injected:
    print(f"Injected back button into: {', '.join(injected)}")

cards = [card_for(p) for p in pages]

cards_json = json.dumps(cards)
taglines_json = json.dumps(TAGLINES)
emojis_json = json.dumps(EMOJIS)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Games 🎮✨</title>
<style>
  :root {{
    --bg-a: #1a0033;
    --bg-b: #2d0066;
    --bg-c: #ff006e;
    --ink: #fff5e1;
    --muted: #c9b8ff;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: ui-rounded, "SF Pro Rounded", "Segoe UI", system-ui, sans-serif;
    color: var(--ink);
    background:
      radial-gradient(ellipse at 20% 10%, #ff006e22, transparent 50%),
      radial-gradient(ellipse at 80% 90%, #00f5d422, transparent 50%),
      linear-gradient(135deg, var(--bg-a), var(--bg-b) 60%, #000);
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }}
  body::before {{
    content: "";
    position: fixed;
    inset: -50%;
    background:
      conic-gradient(from 0deg, #ff006e22, #8338ec22, #3a86ff22, #06ffa522, #ffbe0b22, #ff006e22);
    filter: blur(80px);
    animation: spin 40s linear infinite;
    z-index: -2;
    opacity: 0.55;
  }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

  /* Floating background emojis */
  .float {{
    position: fixed;
    top: 0; left: 0;
    pointer-events: none;
    font-size: 2.4rem;
    opacity: 0.18;
    animation: drift linear infinite;
    z-index: -1;
    user-select: none;
  }}
  @keyframes drift {{
    from {{ transform: translate(var(--x), 110vh) rotate(0deg); }}
    to   {{ transform: translate(calc(var(--x) + var(--drift)), -10vh) rotate(720deg); }}
  }}

  header {{
    text-align: center;
    padding: 4rem 1.5rem 2rem;
    position: relative;
    z-index: 1;
  }}
  h1 {{
    font-size: clamp(2.8rem, 9vw, 6.5rem);
    line-height: 1;
    margin: 0;
    font-weight: 900;
    letter-spacing: -0.03em;
    filter: drop-shadow(0 6px 30px #ff006e88);
  }}
  h1 .ch {{
    display: inline-block;
    background: linear-gradient(180deg, #fff, #ffbe0b 40%, #ff006e 70%, #8338ec);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: wobble 2.5s ease-in-out infinite;
  }}
  h1 .space {{ display: inline-block; width: 0.35em; }}
  @keyframes wobble {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    25% {{ transform: translateY(-8px) rotate(-3deg); }}
    50% {{ transform: translateY(0) rotate(2deg); }}
    75% {{ transform: translateY(6px) rotate(-1deg); }}
  }}
  .tagline {{
    margin: 1rem auto 0;
    font-size: clamp(1rem, 2.2vw, 1.4rem);
    color: var(--muted);
    font-style: italic;
    min-height: 1.6em;
    max-width: 30em;
    transition: opacity 0.4s;
  }}
  .stats {{
    margin-top: 1.4rem;
    display: inline-block;
    padding: 0.4rem 1.1rem;
    border-radius: 999px;
    background: #ffffff15;
    border: 1px solid #ffffff25;
    backdrop-filter: blur(10px);
    font-size: 0.95rem;
    color: var(--ink);
  }}
  .stats b {{ color: #ffbe0b; }}

  main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem 6rem;
    position: relative;
    z-index: 1;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.5rem;
  }}
  .card {{
    --hue: 280;
    position: relative;
    display: block;
    padding: 1.6rem 1.4rem 1.4rem;
    border-radius: 22px;
    text-decoration: none;
    color: var(--ink);
    background:
      linear-gradient(135deg,
        hsla(var(--hue), 90%, 60%, 0.25),
        hsla(calc(var(--hue) + 60), 90%, 50%, 0.15));
    border: 1.5px solid hsla(var(--hue), 90%, 70%, 0.4);
    backdrop-filter: blur(14px);
    overflow: hidden;
    transition: transform 0.25s cubic-bezier(.2,.9,.3,1.4), box-shadow 0.3s;
    transform-style: preserve-3d;
    cursor: pointer;
    animation: cardIn 0.6s backwards cubic-bezier(.2,.9,.3,1.2);
  }}
  @keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(30px) scale(0.9); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}
  .card::before {{
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: 22px;
    background: conic-gradient(from 0deg,
      hsl(var(--hue), 90%, 60%),
      hsl(calc(var(--hue) + 120), 90%, 60%),
      hsl(calc(var(--hue) + 240), 90%, 60%),
      hsl(var(--hue), 90%, 60%));
    opacity: 0;
    transition: opacity 0.4s;
    z-index: -1;
    filter: blur(12px);
  }}
  .card:hover {{
    transform: translateY(-6px) scale(1.03) rotate(-0.5deg);
    box-shadow: 0 20px 50px hsla(var(--hue), 90%, 50%, 0.5);
  }}
  .card:hover::before {{ opacity: 0.9; }}
  .card:active {{ transform: translateY(-2px) scale(0.99); }}
  .card .emoji {{
    font-size: 3.6rem;
    line-height: 1;
    display: inline-block;
    transition: transform 0.4s cubic-bezier(.2,.9,.3,1.6);
    filter: drop-shadow(0 4px 10px #00000066);
  }}
  .card:hover .emoji {{
    transform: scale(1.25) rotate(-12deg);
  }}
  .card h2 {{
    margin: 0.8rem 0 0.3rem;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.01em;
  }}
  .card p {{
    margin: 0;
    font-size: 0.92rem;
    color: #fff8;
    line-height: 1.4;
  }}
  .card .play {{
    margin-top: 1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: hsl(var(--hue), 100%, 85%);
  }}
  .card .arrow {{
    transition: transform 0.3s;
  }}
  .card:hover .arrow {{ transform: translateX(6px); }}

  .empty {{
    text-align: center;
    padding: 4rem 1rem;
    color: var(--muted);
    font-size: 1.2rem;
  }}
  .empty .big {{
    font-size: 5rem;
    margin-bottom: 1rem;
    animation: wobble 2s ease-in-out infinite;
  }}

  footer {{
    text-align: center;
    padding: 2rem 1rem 3rem;
    color: #fff7;
    font-size: 0.9rem;
    position: relative;
    z-index: 1;
  }}
  footer a {{ color: #ffbe0b; }}

  /* Sparkle cursor trail */
  .sparkle {{
    position: fixed;
    pointer-events: none;
    font-size: 1.2rem;
    z-index: 9999;
    animation: poof 0.8s ease-out forwards;
  }}
  @keyframes poof {{
    0%   {{ opacity: 1; transform: translate(-50%, -50%) scale(0.5) rotate(0deg); }}
    100% {{ opacity: 0; transform: translate(-50%, -150%) scale(1.4) rotate(180deg); }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
      animation-duration: 0.001ms !important;
      transition-duration: 0.001ms !important;
    }}
  }}
</style>
</head>
<body>

<header>
  <h1 id="title" aria-label="Games"></h1>
  <p class="tagline" id="tagline">loading vibes…</p>
  <div class="stats">
    <b id="count">{len(cards)}</b> game{("" if len(cards) == 1 else "s")} · all in one <code>.html</code> each · pure chaos
  </div>
</header>

<main>
"""

if cards:
    html += '  <div class="grid">\n'
    for i, c in enumerate(cards):
        desc_html = f'<p>{escape(c["desc"])}</p>' if c["desc"] else ""
        html += f'''    <a class="card" href="{escape(c["href"])}" style="--hue: {c["hue"]}; animation-delay: {i * 0.06:.2f}s;">
      <span class="emoji">{c["emoji"]}</span>
      <h2>{escape(c["title"])}</h2>
      {desc_html}
      <span class="play">Play <span class="arrow">→</span></span>
    </a>
'''
    html += '  </div>\n'
else:
    html += '''  <div class="empty">
    <div class="big">🫥</div>
    <p>No games here yet. Drop a <code>.html</code> file in the root and watch this page bloom.</p>
  </div>
'''

html += f"""</main>

<footer>
  built with ✨ vibes ✨ ·
  <a href="https://github.com/aeskildsen/games" target="_blank" rel="noopener">source</a> ·
  press <kbd>?</kbd> if you dare
</footer>

<script>
  // Splash the title with per-letter wobble
  (function() {{
    const text = "Games";
    const el = document.getElementById('title');
    let html = '';
    [...text].forEach((ch, i) => {{
      if (ch === ' ') {{ html += '<span class="space"></span>'; return; }}
      html += `<span class="ch" style="animation-delay: ${{i * 0.08}}s">${{ch}}</span>`;
    }});
    el.innerHTML = html;
  }})();

  // Rotating taglines
  (function() {{
    const lines = {taglines_json};
    const el = document.getElementById('tagline');
    let i = Math.floor(Math.random() * lines.length);
    el.textContent = lines[i];
    setInterval(() => {{
      el.style.opacity = '0';
      setTimeout(() => {{
        i = (i + 1 + Math.floor(Math.random() * (lines.length - 1))) % lines.length;
        el.textContent = lines[i];
        el.style.opacity = '1';
      }}, 400);
    }}, 4200);
  }})();

  // Floating background emojis
  (function() {{
    const emojis = {emojis_json};
    const n = Math.min(18, Math.max(8, Math.floor(window.innerWidth / 110)));
    for (let i = 0; i < n; i++) {{
      const el = document.createElement('div');
      el.className = 'float';
      el.textContent = emojis[Math.floor(Math.random() * emojis.length)];
      const x = Math.random() * 100;
      el.style.setProperty('--x', x + 'vw');
      el.style.setProperty('--drift', (Math.random() * 30 - 15) + 'vw');
      el.style.fontSize = (1.5 + Math.random() * 2.5) + 'rem';
      el.style.animationDuration = (18 + Math.random() * 22) + 's';
      el.style.animationDelay = (-Math.random() * 30) + 's';
      document.body.appendChild(el);
    }}
  }})();

  // Sparkle cursor trail
  (function() {{
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (matchMedia('(hover: none)').matches) return;
    const sparkles = ['✨', '⭐', '💫', '🌟', '✦'];
    let last = 0;
    window.addEventListener('mousemove', e => {{
      const now = Date.now();
      if (now - last < 60) return;
      last = now;
      const s = document.createElement('div');
      s.className = 'sparkle';
      s.textContent = sparkles[Math.floor(Math.random() * sparkles.length)];
      s.style.left = e.clientX + 'px';
      s.style.top = e.clientY + 'px';
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 800);
    }});
  }})();

  // Card tilt on mouse move
  (function() {{
    document.querySelectorAll('.card').forEach(card => {{
      card.addEventListener('mousemove', e => {{
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = `translateY(-6px) scale(1.03) rotateX(${{-y * 8}}deg) rotateY(${{x * 10}}deg)`;
      }});
      card.addEventListener('mouseleave', () => {{
        card.style.transform = '';
      }});
    }});
  }})();

  // Easter egg: press ? for a surprise
  (function() {{
    document.addEventListener('keydown', e => {{
      if (e.key !== '?') return;
      const burst = ['🎉', '🎊', '🥳', '🪅', '💥', '🦄'];
      for (let i = 0; i < 60; i++) {{
        const s = document.createElement('div');
        s.className = 'sparkle';
        s.style.fontSize = (1 + Math.random() * 2.5) + 'rem';
        s.textContent = burst[Math.floor(Math.random() * burst.length)];
        s.style.left = (Math.random() * window.innerWidth) + 'px';
        s.style.top = (Math.random() * window.innerHeight) + 'px';
        document.body.appendChild(s);
        setTimeout(() => s.remove(), 800);
      }}
    }});
  }})();
</script>
</body>
</html>
"""

Path("index.html").write_text(html, encoding="utf-8")
print(f"Wrote index.html with {len(cards)} link(s).")
