import psutil
VENV_PY = r"C:\\net\\backend\\venv\\Scripts\\python.exe"
pattern = 'start_server.py'
found = 0
for proc in psutil.process_iter(['pid','exe','cmdline']):
    try:
        exe = proc.info.get('exe') or ''
        cmd = ' '.join(proc.info.get('cmdline') or [])
        if exe and exe.lower() == VENV_PY.lower() and pattern in cmd:
            print('Killing PID', proc.pid, 'cmd:', cmd)
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print('  terminated')
            except psutil.TimeoutExpired:
                proc.kill()
                print('  killed')
            found += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

print('Done. Killed', found, 'processes.')
