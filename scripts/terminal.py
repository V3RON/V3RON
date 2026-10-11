"""Generate assets/terminal.svg: an animated zsh window for the profile README.

Usage: python3 scripts/terminal.py <GeistMono-Regular.woff2> assets/terminal.svg

Geist Mono (OFL) is embedded so the SVG renders the same everywhere; get the woff2 from
https://github.com/vercel/geist-font. Edit LINES below to change the copy.
"""
import base64
import sys
from html import escape

FONT_PATH, OUT = sys.argv[1], sys.argv[2]

BG = "#0a0a0a"
TEXT = "#ffffff"
MUTED = "#a2a2a2"   # white at 62% on BG
FAINT = "#858585"   # white at 50% on BG
ACCENT = "#ff4f7b"
ON_ACCENT = "#0a0a0a"

W = 880
PAD_X = 28
BAR_H = 40
TOP = BAR_H + 34          # first baseline
LH = 24                   # line height
FS = 14
CW = FS * 0.6             # monospace advance
LOOP = 18.0               # seconds per loop
TYPE = 0.055              # seconds per typed character

# Each line is a list of (text, colour) runs; command lines start with "$ ".
P = [("$ ", ACCENT)]
LINES = [
    ("cmd", P + [("whoami", TEXT)]),
    ("out", [("Szymon Chmal", TEXT)]),
    ("out", [("Incubator (R&D) Lead at Callstack · Microsoft MVP", MUTED)]),
    ("gap", []),
    ("cmd", P + [("ls", TEXT), (" ~/oss", MUTED)]),
    ("out", [("rozenite   ", TEXT), ("DevTools plugins for React Native, web and agents", MUTED)]),
    ("out", [("voltra     ", TEXT), ("Live Activities and widgets, rendered on the server", MUTED)]),
    ("out", [("harness    ", TEXT), ("Native module tests without mocks, written like Jest", MUTED)]),
    ("out", [("appduct    ", TEXT), ("Your running app as an MCP server for agents and tests", MUTED)]),
    ("out", [("simlock    ", TEXT), ("Simulator leases, so parallel agents stop colliding", MUTED)]),
    ("gap", []),
    ("cmd", P + [("cat", TEXT), (" ~/talks.txt", MUTED)]),
    ("out", [("50+ talks on React Native internals, DevTools, testing,", MUTED)]),
    ("out", [("AI-SDLC and Software Factories, including:", MUTED)]),
    ("out", [("WeAreDevelopers World Congress   ", TEXT), ("DE", FAINT)]),
    ("out", [("Chain React                      ", TEXT), ("US", FAINT)]),
    ("out", [("React Miami                      ", TEXT), ("US", FAINT)]),
    ("out", [("React Native Connection          ", TEXT), ("FR", FAINT)]),
    ("out", [("React Universe Conf              ", TEXT), ("PL", FAINT)]),
    ("gap", []),
    ("cmd", P + [("cat", TEXT), (" ~/coffee.txt", MUTED)]),
    ("out", [("Like the tools? Buy me a coffee: ", MUTED), ("github.com/sponsors/v3ron", ACCENT)]),
    ("end", P),
]

H = TOP + (len(LINES) - 1) * LH + 26


def pct(t):
    return f"{min(t / LOOP * 100, 93.9):.2f}"


# Timeline: when each line appears, and how long a command takes to type.
t = 0.6
shown = []
for kind, runs in LINES:
    if kind == "cmd":
        typed = sum(len(s) for s, _ in runs) - 2
        shown.append((t, t + typed * TYPE, typed))
        t += typed * TYPE + 0.35
    elif kind == "out":
        shown.append((t, None, 0))
        t += 0.09
    elif kind == "gap":
        shown.append((None, None, 0))
        t += 0.8
    else:
        shown.append((t, None, 0))
assert t < LOOP * 0.8, "timeline does not fit the loop"

css = [
    f"@font-face{{font-family:'Geist Mono';src:url(data:font/woff2;base64,"
    f"{base64.b64encode(open(FONT_PATH, 'rb').read()).decode()}) format('woff2')}}",
    "text{font-family:'Geist Mono',ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
    f"'Liberation Mono',monospace;font-size:{FS}px;white-space:pre}}",
    ".bar text{font-size:11px;letter-spacing:.08em}",
    f"@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}",
    ".cur{animation:blink 1.1s step-end infinite}",
]
body = []
defs = []
for i, ((kind, runs), (start, typed_end, n)) in enumerate(zip(LINES, shown)):
    if start is None:
        continue
    y = TOP + i * LH
    css.append(
        f"@keyframes s{i}{{0%,{pct(start)}%{{opacity:0}}{float(pct(start)) + 0.06:.2f}%,94%{{opacity:1}}"
        f"97%,100%{{opacity:0}}}}.l{i}{{animation:s{i} {LOOP}s infinite}}"
    )
    tspans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in runs)
    if kind == "cmd":
        full = (sum(len(s) for s, _ in runs) - 2) * CW + 2
        x0 = PAD_X + 2 * CW
        css.append(
            f"@keyframes w{i}{{0%,{pct(start)}%{{width:0;animation-timing-function:steps({n},end)}}"
            f"{pct(typed_end)}%,100%{{width:{full:.1f}px}}}}.c{i}{{animation:w{i} {LOOP}s infinite}}"
        )
        defs.append(
            f'<clipPath id="k{i}"><rect class="c{i}" x="{x0:.1f}" y="{y - 18}" width="{full:.1f}" height="{LH}"/></clipPath>'
        )
        prompt = f'<text x="{PAD_X}" y="{y}" fill="{ACCENT}">$ </text>'
        rest = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in runs[1:])
        body.append(
            f'<g class="l{i}">{prompt}<text x="{x0:.1f}" y="{y}" clip-path="url(#k{i})">{rest}</text></g>'
        )
    elif kind == "end":
        cx = PAD_X + 2 * CW
        body.append(
            f'<g class="l{i}"><text x="{PAD_X}" y="{y}" fill="{ACCENT}">$ </text>'
            f'<rect class="cur" x="{cx:.1f}" y="{y - 13}" width="{CW:.1f}" height="17" fill="{ACCENT}"/></g>'
        )
    else:
        body.append(f'<text class="l{i}" x="{PAD_X}" y="{y}">{tspans}</text>')

css.append(
    "@media (prefers-reduced-motion:reduce){[class^=l],[class^=c],.cur{animation:none!important}}"
)

# Window bar: accent tag, title, window controls.
tag_w = 5 * 11 * 0.6 + 11 * 0.08 * 5 + 14
bar = (
    f'<g class="bar">'
    f'<rect x="{PAD_X - 8}" y="12" width="{tag_w:.1f}" height="17" fill="{ACCENT}"/>'
    f'<text x="{PAD_X - 1}" y="24.5" fill="{ON_ACCENT}">V3RON</text>'
    f'<text x="{PAD_X - 8 + tag_w + 12:.1f}" y="24.5" fill="{FAINT}">ZSH</text>'
    f'<text x="{W - PAD_X - 64}" y="24.5" fill="{FAINT}">–   □   ×</text>'
    f"</g>"
)

label = (
    "Terminal. whoami: Szymon Chmal, Incubator (R&D) Lead at Callstack, Microsoft MVP. "
    "ls ~/oss: rozenite, voltra, harness, appduct, simlock. "
    "cat ~/talks.txt: 50+ talks on React Native internals, DevTools, testing, AI-SDLC and Software Factories, including "
    "WeAreDevelopers World Congress (DE), Chain React (US), React Miami (US), "
    "React Native Connection (FR) and React Universe Conf (PL). "
    "cat ~/coffee.txt: Like the tools? Buy me a coffee: github.com/sponsors/v3ron"
)
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="{escape(label)}">'
    f"<title>{escape(label)}</title>"
    f"<style>{''.join(css)}</style>"
    f"<defs>{''.join(defs)}</defs>"
    f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{BG}" stroke="#ffffff" stroke-opacity=".16"/>'
    f'<path d="M1 {BAR_H}.5H{W - 1}" stroke="#ffffff" stroke-opacity=".08"/>'
    f"{bar}{''.join(body)}</svg>\n"
)
open(OUT, "w").write(svg)
print(f"wrote {OUT}: {W}x{H}, {len(svg)} bytes, timeline ends at {t:.1f}s of {LOOP}s")
