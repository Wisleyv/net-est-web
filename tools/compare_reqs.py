from pathlib import Path
import re


def normalize_line(s: str) -> str:
    # strip common BOMs and nulls
    s = s.replace('\ufeff', '').replace('\ufffe', '').replace('\x00', '')
    # strip weird leading latin1-decoded utf-16 markers like 'ÿþ'
    s = re.sub(r'^[\s\W\x80-\xFF]+', '', s)
    return s.strip()


def parse_lines(text_lines):
    items = {}
    for line in text_lines:
        s = normalize_line(line)
        if not s or s.startswith('```') or s == '==' or s == '':
            continue
        # handle VCS or URL lines with ' @ '
        if ' @ ' in s and '==' not in s:
            name, rest = s.split(' @ ', 1)
            items[name.strip().lower()] = (name.strip(), rest.strip())
            continue

        # Many pip freeze outputs are 'name==version'. Some broken reads may add extra '='
        if '==' in s:
            parts = s.split('==')
            name = parts[0].strip()
            ver = '=='.join(parts[1:]).strip()
            # drop any trailing stray '=' characters
            ver = ver.rstrip('=')
            items[name.lower()] = (name, ver)
        else:
            # fallback: treat whole line as name with empty version
            items[s.lower()] = (s, '')
    return items


def read_lines_safe(p):
    path = Path(p)
    # try utf-8 first, then utf-16, then latin-1
    for enc in ('utf-8', 'utf-16', 'latin-1'):
        try:
            txt = path.read_text(encoding=enc)
        except Exception:
            continue
        # quick heuristic: if file looks like UTF-16 decoded as latin-1, there will be many nulls
        if '\x00' in txt and enc != 'utf-16':
            # try utf-16 explicitly
            try:
                txt = path.read_text(encoding='utf-16')
            except Exception:
                pass
        # split into lines and return
        return txt.splitlines()
    # last resort
    return path.read_text(encoding='latin-1', errors='replace').splitlines()


def format_pair(name, ver):
    return f"{name}=={ver}" if ver else name


base = read_lines_safe('current_requirements.txt')
new = read_lines_safe('pip_list_py312.txt')
mapA = parse_lines(base)
mapB = parse_lines(new)
removed = []
added = []
changed = []

for k, v in sorted(mapA.items()):
    if k not in mapB:
        removed.append(format_pair(v[0], v[1]))
    else:
        if v[1] != mapB[k][1]:
            changed.append((v[0], v[1], mapB[k][1]))
for k, v in sorted(mapB.items()):
    if k not in mapA:
        added.append(format_pair(v[0], v[1]))

print('*** Compact patch-style diff between current_requirements.txt and pip_list_py312.txt')
print('\n--- removed (in current_requirements.txt but NOT in pip_list_py312.txt):')
for r in removed:
    print('- ' + r)
print('\n+++ added (in pip_list_py312.txt but NOT in current_requirements.txt):')
for a in added:
    print('+ ' + a)
print('\n*** changed (same package, version different):')
for c in changed:
    print('~ {} : {} -> {}'.format(c[0], c[1], c[2]))
