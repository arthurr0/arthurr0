"""
Generator neofetch-README dla github.com/arthurr0

Tworzy assets/dark_mode.svg + assets/light_mode.svg + README.md
GitHub NIE renderuje kolorow ANSI w blokach kodu - dlatego SVG.

Uruchom:  python3 generate_readme.py
Opcje:    --strict   przerwij z bledem, gdy GitHub API jest niedostepne
Env:      GITHUB_TOKEN  podnosi limit API i odblokowuje liste pinned
          README_OUT    katalog docelowy (domyslnie katalog skryptu)
"""
import calendar, html, json, os, sys, urllib.error, urllib.request
from datetime import datetime, timezone

USER    = "arthurr0"
BASE    = os.path.dirname(os.path.abspath(__file__))
OUT     = os.environ.get("README_OUT", BASE)
ASSETS  = os.path.join(OUT, "assets")
TOKEN   = os.environ.get("GITHUB_TOKEN", "").strip()
STRICT  = "--strict" in sys.argv
TZ_NAME = "Europe/Warsaw"

ART_W     = 41
W     = 56

PALETTES = {
    "dark": {
        "key": "#c792ea", "val": "#56d4dd", "dot": "#484f58",
        "tit": "#e6edf3", "grn": "#7ee787", "red": "#ff7b72",
        "art": "#79b8ff",
    },
    "light": {
        "key": "#8250df", "val": "#0550ae", "dot": "#afb8c1",
        "tit": "#1f2328", "grn": "#1a7f37", "red": "#cf222e",
        "art": "#0969da",
    },
}

FALLBACK = {
    "created_at":   "2020-02-18T00:00:00Z",
    "public_repos": 17,
    "followers":    29,
    "following":    16,
    "starred":      66,
    "pinned":       ["minecraft-cli-admin", "mTerminal"],
}

critical_failures = []

def log(msg):
    print(msg, file=sys.stderr)

def api(url, payload=None):
    req = urllib.request.Request(url, data=payload, method="POST" if payload else "GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"{USER}-readme-generator")
    if payload:
        req.add_header("Content-Type", "application/json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8")), r.headers

def last_page(headers):
    link = headers.get("Link", "")
    for part in link.split(","):
        if 'rel="last"' in part:
            href = part.split(";")[0].strip().strip("<>")
            for kv in href.split("?", 1)[-1].split("&"):
                if kv.startswith("page="):
                    return int(kv[5:])
    return None

def fetch_profile(stats):
    data, _ = api(f"https://api.github.com/users/{USER}")
    stats["created_at"]   = data["created_at"]
    stats["public_repos"] = data["public_repos"]
    stats["followers"]    = data["followers"]
    stats["following"]    = data["following"]

def fetch_starred(stats):
    data, headers = api(f"https://api.github.com/users/{USER}/starred?per_page=1")
    stats["starred"] = last_page(headers) or len(data)

def fetch_pinned(stats):
    if not TOKEN:
        raise RuntimeError("brak GITHUB_TOKEN - GraphQL wymaga autoryzacji")
    query = ('{ user(login: "%s") { pinnedItems(first: 6, types: REPOSITORY) '
             '{ nodes { ... on Repository { name } } } } }' % USER)
    payload = json.dumps({"query": query}).encode("utf-8")
    data, _ = api("https://api.github.com/graphql", payload)
    if "errors" in data:
        raise RuntimeError(data["errors"][0].get("message", "blad GraphQL"))
    nodes = data["data"]["user"]["pinnedItems"]["nodes"]
    names = [n["name"] for n in nodes if n]
    if names:
        stats["pinned"] = names

def collect():
    stats = dict(FALLBACK)
    for name, fn, critical in (("profil", fetch_profile, True),
                               ("starred", fetch_starred, True),
                               ("pinned", fetch_pinned, False)):
        try:
            fn(stats)
            log(f"api: {name} OK")
        except Exception as exc:
            if critical:
                critical_failures.append(name)
            log(f"api: {name} NIEUDANE ({exc}) - uzywam wartosci awaryjnej")
    return stats

S = collect()

def uptime(created_iso):
    start = datetime.strptime(created_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now   = datetime.now(timezone.utc)
    y = now.year - start.year
    m = now.month - start.month
    d = now.day - start.day
    if d < 0:
        m -= 1
        pm = now.month - 1 or 12
        py = now.year if now.month > 1 else now.year - 1
        d += calendar.monthrange(py, pm)[1]
    if m < 0:
        y -= 1
        m += 12
    def unit(n, word):
        return f"{n} {word}" if n == 1 else f"{n} {word}s"
    return f"{unit(y, 'year')}, {unit(m, 'month')}, {unit(d, 'day')}"

def local_offset():
    try:
        from zoneinfo import ZoneInfo
        off = datetime.now(ZoneInfo(TZ_NAME)).utcoffset()
        total = int(off.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        return f"UTC{sign}{total // 3600:02d}:{total % 3600 // 60:02d}"
    except Exception as exc:
        log(f"strefa czasowa: NIEUDANE ({exc}) - uzywam UTC+01:00")
        return "UTC+01:00"

def fit(items, limit):
    picked, used = [], 0
    for i, item in enumerate(items):
        extra = len(item) + (2 if picked else 0)
        if picked and used + extra > limit:
            rest = len(items) - i
            tail = f", +{rest}"
            while picked and used + len(tail) > limit:
                used -= len(picked[-1]) + (2 if len(picked) > 1 else 0)
                picked.pop()
            return ", ".join(picked) + tail
        picked.append(item)
        used += extra
    return ", ".join(picked)

lines = []
info  = []

def head(title):
    left = f"{title} "
    info.append([(left, "tit"), ("-" * max(1, W - len(left)), "dot")])

def sec(title):
    left = f"- {title} "
    info.append([(left, "tit"), ("-" * max(1, W - len(left)), "dot")])

def row(key, value, vrole="val"):
    left = f"- {key}:"
    n = max(1, W - len(left) - len(value) - 2)
    info.append([(left, "key"), (" ", "dot"), ("." * n, "dot"),
                 (" ", "dot"), (value, vrole)])

def raw(key, plain, segs):
    left = f"- {key}:"
    n = max(1, W - len(left) - len(plain) - 2)
    info.append([(left, "key"), (" ", "dot"), ("." * n, "dot"),
                 (" ", "dot")] + segs)

def blank():
    info.append([])

def room_for(key):
    return W - len(f"- {key}:") - 2

head("arthurr0@github")
row("OS", "CachyOS, iOS")
row("Uptime", uptime(S["created_at"]))
row("Host", "minecodes.pl / mLicense.net")
row("Kernel", "Full Stack Developer")
row("Shell", f"Warsaw, Poland ({local_offset()})")
row("IDE", "IntelliJ IDEA, Terminal")
blank()

row("Stack.Backend", "Java, Spring Boot, Hibernate")
row("Stack.Frontend", "Vue.js, Nuxt, Angular, Tailwind CSS")
row("Stack.Languages", "Java, TypeScript, JavaScript")
row("Stack.Databases", "PostgreSQL, MySQL, MongoDB")
row("Stack.DevOps", "Docker, Maven, Gradle, CI/CD")
row("Languages.Real", "Polish, English")
blank()

row("Focus", "Backend, AI Integration, EAI Integration")
row("Interests", "Linux, AI, Fishing")
blank()

sec("Contact")
row("GitHub", "github.com/arthurr0")
row("Website", "minecodes.pl")
row("Organization", "mineCodes")
row("Email", "biuro@minecodes.pl")
blank()

sec("GitHub Stats")
repos, stars = str(S["public_repos"]), str(S["starred"])
raw("Repos", f"{repos} {{Stars given: {stars}}}",
    [(repos, "val"), (" ", "dot"), ("{", "dot"), ("Stars given: ", "key"),
     (stars, "val"), ("}", "dot")])
followers, following = str(S["followers"]), str(S["following"])
raw("Followers", f"{followers} | Following: {following}",
    [(followers, "val"), (" | ", "dot"), ("Following: ", "key"),
     (following, "val")])
raw("Achievements", "Pull Shark x3, Quickdraw, YOLO",
    [("Pull Shark x3", "grn"), (", ", "dot"), ("Quickdraw", "grn"),
     (", ", "dot"), ("YOLO", "grn")])
row("Pinned", fit(S["pinned"], room_for("Pinned")))

art = r"""
   .--------------------------------.
   | * * *              ~/arthurr0  |
   |--------------------------------|
   |                                |
   |  $ whoami                      |
   |  > artur kolecki               |
   |                                |
   |  $ cat stack.txt               |
   |  > java . spring . vue         |
   |  > typescript . docker         |
   |                                |
   |  $ ./deploy.sh                 |
   |  > building things _           |
   |                                |
   |                                |
   '--------------------------------'
""".strip("\n").split("\n")

for i in range(max(len(art), len(info))):
    a = art[i] if i < len(art) else ""
    b = info[i] if i < len(info) else []
    segs = []
    if a.strip():
        segs.append((a.ljust(ART_W), "art"))
    else:
        segs.append((" " * ART_W, "dot"))
    segs.extend(b)
    lines.append(segs)

FONT_SIZE = 14
LINE_H    = 20
PAD_X     = 12
PAD_Y     = 14
CHAR_W    = 8.4
MAXCOLS   = max(sum(len(t) for t, _ in l) for l in lines)
WIDTH     = int(PAD_X * 2 + MAXCOLS * CHAR_W) + 8
HEIGHT    = PAD_Y * 2 + len(lines) * LINE_H

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', 'DejaVu Sans Mono', monospace")

def render(theme):
    p = PALETTES[theme]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'font-family="{FONT}" font-size="{FONT_SIZE}">',
        '<style>text{white-space:pre}</style>',
    ]
    for i, segs in enumerate(lines):
        if not any(t.strip() for t, _ in segs):
            continue
        y = PAD_Y + (i + 1) * LINE_H - 5
        parts, col = [], 0
        for t, role in segs:
            k = 0
            while k < len(t):
                if t[k] == " ":
                    k += 1
                    continue
                j = k
                while j < len(t) and t[j] != " ":
                    j += 1
                run = t[k:j]
                xs = " ".join(f"{PAD_X + (col + k + m) * CHAR_W:.1f}"
                              for m in range(len(run)))
                parts.append(f'<tspan x="{xs}" fill="{p[role]}">'
                             f'{html.escape(run)}</tspan>')
                k = j
            col += len(t)
        out.append(f'<text y="{y}">' + "".join(parts) + '</text>')
    out.append('</svg>')
    return "\n".join(out)

os.makedirs(ASSETS, exist_ok=True)
for theme in ("dark", "light"):
    with open(os.path.join(ASSETS, f"{theme}_mode.svg"), "w", encoding="utf-8") as f:
        f.write(render(theme))

readme = """<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/dark_mode.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/light_mode.svg">
  <img alt="arthurr0's GitHub profile" src="assets/dark_mode.svg">
</picture>
"""
with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

print(f"OK  {WIDTH}x{HEIGHT}px, {len(lines)} linii, {MAXCOLS} kolumn")

if critical_failures and STRICT:
    log(f"BLAD: nieudane pobrania: {', '.join(critical_failures)}")
    sys.exit(1)
