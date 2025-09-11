/*
  Starts the FastAPI backend for Playwright E2E on Windows reliably.
  - If port 8000 is already open, exit 0 so Playwright reuses it.
  - Otherwise, spawn the venv python to run uvicorn and wait until ready.
  - Pass through environment variables from Playwright webServer.env.
*/

const fs = require('fs');
const path = require('path');
const net = require('net');
const { spawn } = require('child_process');

const HOST = '127.0.0.1';
const PORT = 8000;
const BACKEND_CWD = path.join(__dirname, '..', '..', 'backend');
const PYTHON_EXE = path.join(BACKEND_CWD, 'venv', 'Scripts', 'python.exe');

function isPortOpen(host, port, timeoutMs = 1000) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    const onError = () => {
      try { socket.destroy(); } catch {}
      resolve(false);
    };
    socket.setTimeout(timeoutMs);
    socket.once('error', onError);
    socket.once('timeout', onError);
    socket.connect(port, host, () => {
      try { socket.end(); } catch {}
      resolve(true);
    });
  });
}

async function waitForPort(host, port, totalTimeoutMs = 120_000, intervalMs = 500) {
  const start = Date.now();
  while (Date.now() - start < totalTimeoutMs) {
    // eslint-disable-next-line no-await-in-loop
    if (await isPortOpen(host, port)) return true;
    // eslint-disable-next-line no-await-in-loop
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

(async () => {
  if (await isPortOpen(HOST, PORT)) {
    console.log(`[start-backend] Backend already running at http://${HOST}:${PORT}`);
    process.exit(0);
  }

  if (!fs.existsSync(PYTHON_EXE)) {
    console.error('[start-backend] Missing backend virtual environment python:', PYTHON_EXE);
    console.error('[start-backend] Please run the VS Code task: "Setup Backend Environment"');
    process.exit(1);
  }

  console.log('[start-backend] Starting backend via uvicorn...');
  const child = spawn(PYTHON_EXE, [
    '-m', 'uvicorn', 'src.main:app',
    '--host', HOST,
    '--port', String(PORT),
    '--log-level', 'warning',
  ], {
    cwd: BACKEND_CWD,
    env: { ...process.env },
    stdio: ['ignore', 'inherit', 'inherit'],
    windowsHide: true,
  });

  let exited = false;
  child.on('exit', (code, signal) => {
    exited = true;
    console.error(`[start-backend] Backend process exited early (code=${code} signal=${signal}).`);
  });

  const ready = await waitForPort(HOST, PORT, 120_000, 500);
  if (!ready) {
    console.error('[start-backend] Backend did not become ready within timeout.');
    try { child.kill(); } catch {}
    process.exit(1);
  }

  if (exited) {
    console.error('[start-backend] Backend exited after starting; aborting.');
    process.exit(1);
  }

  console.log(`[start-backend] Backend started at http://${HOST}:${PORT}`);

  const shutdown = () => {
    try { child.kill(); } catch {}
    process.exit(0);
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
  // Keep process alive while child runs
})();
