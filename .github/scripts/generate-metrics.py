import json, os, urllib.request
from collections import defaultdict

TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
USER = os.environ.get('GITHUB_USER','Chandrasen74')
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept':'application/vnd.github+json', 'User-Agent':'metrics-gen'} if TOKEN else {'Accept':'application/vnd.github+json','User-Agent':'metrics-gen'}

def api(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

user = api(f'https://api.github.com/users/{USER}')
repos=[]; page=1
while True:
    batch = api(f'https://api.github.com/user/repos?per_page=100&page={page}&type=owner')
    if not batch: break
    repos += batch
    if len(batch) < 100: break
    page += 1
owned = [r for r in repos if not r.get('fork')]
stars = sum(r.get('stargazers_count',0) for r in owned)
langs = defaultdict(int)
for r in owned:
    try:
        l = api(r['languages_url'])
        for k,v in l.items():
            langs[k]+=int(v)
    except Exception:
        pass
all_sorted = sorted(langs.items(), key=lambda x: x[1], reverse=True)
top = all_sorted[:18]
total_all = sum(v for _,v in all_sorted) or 1
max_v = top[0][1] if top else 1

W=700
left=24; bar_x=180; bar_w=300; bar_h=14; row_h=28
lang_start=170
H = lang_start + row_h*len(top) + 40

lang_colors = {
 'HTML':'#e34c26','CSS':'#563d7c','JavaScript':'#f1e05a','TypeScript':'#3178c6','Kotlin':'#A97BFF',
 'Python':'#3572A5','C++':'#f34b7d','C':'#555555','Java':'#b07219','Shell':'#89e051','Svelte':'#ff3e00','QML':'#44a51c',
 'Cuda':'#3A4E3A','CMake':'#DA3434','Metal':'#8f14e9','Jinja':'#a52a22','GLSL':'#5686a5'
}
def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def fmt(n):
    if n >= 1_000_000: return f'{n/1_000_000:.1f}M'
    if n >= 1_000: return f'{n/1_000:.1f}K'
    return str(n)

parts=[]
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append('<style>')
parts.append('text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;fill:#24292f;font-size:14px}')
parts.append('.title{font-size:18px;font-weight:600}.muted{fill:#57606a;font-size:13px}.val{font-weight:600}.small{font-size:12px;fill:#57606a}')
parts.append('@media (prefers-color-scheme: dark){text{fill:#c9d1d9}.muted,.small{fill:#8b949e}rect.bg{fill:#0d1117}rect.card{fill:#161b22;stroke:#30363d}rect.track{fill:#21262d}}')
parts.append('</style>')
parts.append(f'<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="10" fill="#ffffff"/>')
parts.append(f'<rect class="card" x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="#f6f8fa" stroke="#d0d7de"/>')
parts.append(f'<text class="title" x="{left}" y="40">GitHub Stats</text>')

stats = [
  ("Public repos", user.get('public_repos',0)),
  ("Followers", user.get('followers',0)),
  ("Following", user.get('following',0)),
  ("Stars (owned repos)", stars),
]
sy=70; col_w=160
for i,(label,val) in enumerate(stats):
    x = left + (i%4)*col_w
    parts.append(f'<text class="muted" x="{x}" y="{sy}">{esc(label)}</text>')
    parts.append(f'<text class="val" x="{x}" y="{sy+22}">{esc(fmt(val))}</text>')

parts.append(f'<text class="muted" x="{left}" y="135">Top languages by code in owned non-fork repositories</text>')

for i,(name,val) in enumerate(top):
    y = lang_start + i*row_h
    pct = val/total_all*100
    color = lang_colors.get(name,'#8b949e')
    parts.append(f'<text x="{left}" y="{y}">{esc(name)}</text>')
    parts.append(f'<rect class="track" x="{bar_x}" y="{y-11}" width="{bar_w}" height="{bar_h}" rx="7" fill="#d0d7de"/>')
    fill_w = max(4, int(bar_w*(val/max_v)))
    parts.append(f'<rect x="{bar_x}" y="{y-11}" width="{fill_w}" height="{bar_h}" rx="7" fill="{color}"/>')
    parts.append(f'<text class="small" x="{bar_x+bar_w+12}" y="{y}">{pct:.1f}% ({fmt(val)})</text>')

parts.append(f'<text class="small" x="{left}" y="{H-16}">Auto-generated from GitHub API data.</text>')
parts.append('</svg>')

with open('github-metrics.svg','w',encoding='utf-8') as f:
    f.write('\n'.join(parts))
print('wrote github-metrics.svg')
