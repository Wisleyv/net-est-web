import sys
import socket
import urllib.request
import urllib.error

try:
    import psutil
except Exception as e:
    print('ERROR: psutil not available:', e)
    sys.exit(2)

VENV_PY = r"C:\net\backend\venv\Scripts\python.exe"
print('Searching for processes using:', VENV_PY)
found = []
for proc in psutil.process_iter(['pid', 'exe', 'cmdline']):
    try:
        exe = proc.info.get('exe') or ''
        cmd = proc.info.get('cmdline') or []
        if exe and exe.lower() == VENV_PY.lower():
            print('\nPID:', proc.pid)
            print('  exe:', exe)
            print('  cmdline:', ' '.join(cmd))
            found.append(proc.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

if not found:
    print('\nNo processes found using the backend venv python.')
else:
    print('\nFound', len(found), 'process(es) using the backend venv python.')

# Check for listeners on port 8000
print('\nChecking for listeners on port 8000...')
listening = False
try:
    for conn in psutil.net_connections(kind='inet'):
        laddr = conn.laddr if conn.laddr else None
        if laddr and getattr(laddr, 'port', None) == 8000:
            # status might be 'LISTEN' on Windows
            print('  Found connection: pid=%s status=%s laddr=%s raddr=%s' % (conn.pid, conn.status, laddr, conn.raddr))
            listening = True
except Exception as e:
    print('  Could not enumerate net_connections:', e)

if not listening:
    print('  No listener on port 8000 detected via psutil.')

# HTTP GET /health
print('\nPerforming HTTP GET http://127.0.0.1:8000/health')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/health')
    with urllib.request.urlopen(req, timeout=3) as resp:
        body = resp.read(1024).decode('utf-8', errors='replace')
        print('  STATUS:', resp.getcode())
        print('  BODY:', body)
except urllib.error.HTTPError as e:
    print('  HTTP ERROR:', e.code, e.reason)
except Exception as e:
    print('  ERROR connecting to /health:', e)

print('\nDone')
