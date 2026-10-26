"""Run the unmodified shared deploy CLI in a site-only, vault-free TEMP copy."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import argparse
import sys

sys.stdout.reconfigure(encoding='utf-8')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--prepare-only', action='store_true')
parser.add_argument('--finish', type=Path)
args = parser.parse_args()

site = Path(__file__).resolve().parents[1]
root = args.finish.resolve() if args.finish else Path(tempfile.mkdtemp(prefix='jos24-split-ci-')).resolve()
# 將工具尋找設定的邊界留在隔離根目錄，避免讀取受限的使用者目錄。
(root / 'package.json').write_text('{"type":"module","private":true}\n', encoding='utf-8')
website = root / 'appendix' / 'website'
copy = website / site.parent.name / site.name
if not args.finish:
    copy.mkdir(parents=True)
    for name in ['src', 'data', 'scripts', 'node_modules']:
        shutil.copytree(site / name, copy / name)
    # Alpha gate needs the original cutouts, not the rest of the large lab.
    ledger = json.loads((site / 'src/assets/stations/sources.json').read_text(encoding='utf-8'))
    stations = json.loads((site / 'src/data/stations.json').read_text(encoding='utf-8'))
    for source in {ledger[layer['asset']]['source'] for station in stations for layer in station['layers'] if layer['role'] in ('person', 'coffin')}:
        destination = copy / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(site / source, destination)
    for name in ['package.json', 'package-lock.json', 'vite.config.ts', 'tsconfig.json', 'index.html', 'appendix-chapters.json']:
        shutil.copy2(site / name, copy / name)
builder = website / 'build.py'
shutil.copy2(site.parents[1] / 'build.py', builder)
assert hashlib.sha256(builder.read_bytes()).digest() == hashlib.sha256((site.parents[1] / 'build.py').read_bytes()).digest()
deploy = root / 'deployed'
out = site / '.tmp-shots' / 'loading'
out.mkdir(parents=True, exist_ok=True)
if args.prepare_only:
    (out / 'ci-prepared.json').write_text(json.dumps({'root': str(root), 'builder': str(builder), 'deploy': str(deploy)}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(root)
    raise SystemExit(0)
if not args.finish:
    subprocess.run(['python', '-I', str(builder), '--build', '--deploy-dir', str(deploy)], check=True, cwd=root)
expected = {p.relative_to(site / 'dist').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (site / 'dist').rglob('*') if p.is_file()}
ci = {p.relative_to(copy / 'dist').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (copy / 'dist').rglob('*') if p.is_file()}
deployed = deploy / site.parent.name / site.name
actual = {p.relative_to(deployed).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in deployed.rglob('*') if p.is_file()}
assert expected == ci == actual, 'Local, CI and deployed files differ'
record = {'root': str(root), 'ciRoot': str(copy / 'dist'), 'deployRoot': str(deploy), 'deployPath': f'{site.parent.name}/{site.name}/', 'files': len(actual), 'matching': True, 'dependencyInstall': 'Copied existing node_modules; no network install', 'builderSha256': hashlib.sha256(builder.read_bytes()).hexdigest()}
(out / 'deploy.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
