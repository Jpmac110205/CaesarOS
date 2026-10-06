import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const venv = path.join(root, '.venv-demo');
const venvPython = path.join(venv, process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const requirements = path.join(root, 'requirements.txt');
const fingerprintFile = path.join(venv, '.caesaros-dependencies.sha256');
const versionCheck = 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)';
let child;
let interrupted = false;
let shutdownTimer;

function signalChild(signal) {
  if (!child?.pid) return;
  try {
    // Uvicorn's reload worker belongs to this process group too.
    if (process.platform === 'win32') child.kill(signal);
    else process.kill(-child.pid, signal);
  } catch (error) {
    if (error.code !== 'ESRCH') throw error;
  }
}

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => {
    if (interrupted) return;
    interrupted = true;
    signalChild(signal);
    shutdownTimer = setTimeout(() => signalChild('SIGKILL'), 5000);
    shutdownTimer.unref();
  });
}

function supportsPython(command, args = []) {
  return spawnSync(command, [...args, '-c', versionCheck], {
    cwd: root, stdio: 'ignore', timeout: 10000,
  }).status === 0;
}

function run(command, args) {
  if (interrupted) return Promise.reject(new Error('Startup interrupted.'));
  return new Promise((resolve, reject) => {
    child = spawn(command, args, {
      cwd: root, stdio: 'inherit', env: process.env,
      detached: process.platform !== 'win32',
    });
    child.once('error', reject);
    child.once('close', (code, signal) => {
      child = undefined;
      if (shutdownTimer) clearTimeout(shutdownTimer);
      if (code === 0 && !interrupted) resolve();
      else reject(new Error(`Process stopped (${signal ?? `exit ${code}`}).`));
    });
  });
}

async function main() {
  const port = process.env.CAESAROS_PORT ?? '8000';
  if (!/^\d+$/.test(port) || Number(port) < 1 || Number(port) > 65535) {
    throw new Error('CAESAROS_PORT must be an integer from 1 to 65535.');
  }

  if (!existsSync(venvPython)) {
    const candidates = process.env.CAESAROS_PYTHON
      ? [[process.env.CAESAROS_PYTHON, []]]
      : [['python3', []], ['python', []], ...(process.platform === 'win32' ? [['py', ['-3']]] : [])];
    const python = candidates.find(([command, args]) => supportsPython(command, args));
    if (!python) throw new Error('Python 3.11+ is required. Install it or set CAESAROS_PYTHON to its executable.');
    console.log('Creating the CaesarOS Python environment…');
    await run(python[0], [...python[1], '-m', 'venv', venv]);
  }
  if (!supportsPython(venvPython)) {
    throw new Error('.venv-demo needs Python 3.11+. Recreate it with a supported Python version.');
  }

  const fingerprint = createHash('sha256').update(readFileSync(requirements)).digest('hex');
  const installedFingerprint = existsSync(fingerprintFile) ? readFileSync(fingerprintFile, 'utf8').trim() : '';
  const imports = spawnSync(venvPython, ['-c', 'import fastapi, uvicorn, langgraph, apscheduler, httpx, dotenv, discord'], {
    cwd: root, stdio: 'ignore', timeout: 10000,
  });
  if (installedFingerprint !== fingerprint || imports.status !== 0) {
    console.log('Installing CaesarOS Python dependencies…');
    await run(venvPython, ['-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', '-r', requirements]);
    writeFileSync(fingerprintFile, `${fingerprint}\n`);
  }

  // Check keys without launching a reload supervisor that would linger after an import failure.
  await run(venvPython, ['-c', [
    'import sys',
    'from caesaros.config import Settings',
    'try:',
    '    Settings.from_env()',
    'except (ValueError, KeyError) as error:',
    '    print(f"CaesarOS configuration error: {error}", file=sys.stderr)',
    '    sys.exit(1)',
  ].join('\n')]);

  console.log(`\nCaesarOS dashboard: http://127.0.0.1:${port}`);
  console.log(`API documentation: http://127.0.0.1:${port}/docs`);
  console.log('Backend reload is enabled. Refresh the browser after frontend edits. Press Ctrl+C to stop.\n');
  await run(venvPython, ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', port,
    '--reload', '--reload-dir', 'caesaros', '--reload-dir', 'agents', '--reload-dir', 'backend']);
}

main().catch(error => {
  if (!interrupted) console.error(`\n${error.message}`);
  process.exitCode = interrupted ? 130 : 1;
});
