import subprocess
import os
import sys
LOG = r"C:\net\backend\uvicorn_launch.log"
PY = r"C:\net\backend\venv\Scripts\python.exe"
ARGS = [PY, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"]
print('Starting:', ' '.join(ARGS))
with open(LOG, 'ab') as f:
    p = subprocess.Popen(ARGS, cwd=r"C:\net\backend", stdout=f, stderr=f, close_fds=True)
    print('Launched PID', p.pid)
    print('Log:', LOG)
    sys.stdout.flush()
