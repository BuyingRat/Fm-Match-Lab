"""Keep a compressed copy of every study's results in a private folder (Dropbox by default). Never deletes anything.

  .venv/bin/python scripts/backup_results.py [--dest ~/Dropbox/FM27-Match-Lab-backup]

What is copied, one .tar.gz per item:
  - every folder in runs/ and port/mac_host/runs/ (results, designs, reports, logs), without the scenario files in
    bins/ and the scratch work/ folders, which the studies' build steps regenerate;
  - loose files in those two folders;
  - private/ without private/engine (rebuilt by scripts/setup.py);
  - the backup of FM27's saved matches (src/match_backup.py), which the game itself deletes after ten.

An item is archived again only when one of its files changed (size or time); each version is a new file named with
the date, and older versions are kept. DEST/manifest.json lists every archive with its fingerprint. Free space on
this disk and the destination is printed at the end, with a warning below 30 GB.
"""
import argparse, hashlib, json, shutil, sys, tarfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
SKIP_DIRS = {'bins', 'work', '__pycache__'}
LOW_GB = 30


def files_of(path, skip=()):
    if path.is_file(): return [path]
    out = []
    for p in sorted(path.rglob('*')):
        rel = p.relative_to(path).parts
        if p.is_file() and not any(part in SKIP_DIRS for part in rel[:-1]) and not any(str(p).startswith(str(s)) for s in skip):
            out.append(p)
    return out


def items():
    import match_backup
    for base in (ROOT / 'runs', ROOT / 'port/mac_host/runs'):
        label = base.relative_to(ROOT).as_posix().replace('/', '_')
        loose = [p for p in sorted(base.iterdir()) if p.is_file()]
        if loose: yield f'{label}__loose', base, loose
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            yield f'{label}__{d.name}', base, files_of(d)
    yield 'private', ROOT, files_of(ROOT / 'private', skip=[ROOT / 'private/engine'])
    saved = match_backup.backup_folder()
    yield 'saved_matches', saved.parent, files_of(saved)


def fingerprint(files):
    h = hashlib.sha1()
    for f in files:
        st = f.stat(); h.update(f'{f}\0{st.st_size}\0{int(st.st_mtime)}\n'.encode())
    return h.hexdigest()


def free_gb(path):
    return shutil.disk_usage(path).free / 1e9


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dest', default='~/Dropbox/FM27-Match-Lab-backup')
    a = p.parse_args(); dest = Path(a.dest).expanduser(); dest.mkdir(parents=True, exist_ok=True)
    mf = dest / 'manifest.json'; manifest = json.loads(mf.read_text()) if mf.exists() else {}
    stamp = time.strftime('%Y%m%d-%H%M'); new = same = 0; size = 0
    for name, base, files in items():
        if not files: continue
        fp = fingerprint(files); versions = manifest.setdefault(name, [])
        if versions and versions[-1]['fingerprint'] == fp: same += 1; continue
        target = dest / name / f'{name}__{stamp}.tar.gz'; target.parent.mkdir(exist_ok=True)
        tmp = target.with_suffix('.partial')
        with tarfile.open(tmp, 'w:gz', compresslevel=6) as t:
            for f in files: t.add(f, arcname=f.relative_to(base).as_posix())
        tmp.rename(target); size += target.stat().st_size; new += 1
        versions.append({'file': target.relative_to(dest).as_posix(), 'fingerprint': fp, 'files': len(files),
                         'bytes': sum(f.stat().st_size for f in files), 'archived': stamp})
        mf.write_text(json.dumps(manifest, indent=1))
        print(f'{name}: {len(files)} files -> {target.name} ({target.stat().st_size / 1e6:.1f} MB)', flush=True)
    print(f'{new} archived ({size / 1e6:.0f} MB), {same} unchanged; in {dest}')
    for label, path in (('this disk', ROOT), ('destination', dest)):
        g = free_gb(path); print(f'free on {label}: {g:.0f} GB' + (f'  WARNING: below {LOW_GB} GB' if g < LOW_GB else ''))


if __name__ == '__main__':
    main()
