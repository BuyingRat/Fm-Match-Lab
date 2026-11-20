#!/usr/bin/env python3
"""Struct offsets on the arm64 slice: vote from decompiled twin functions (arm64 timing test).

    python port/map/offset_vote_arch.py select --x86 X86.jsonl --arm ARM.jsonl --pairs PAIRS.json --out DIR
    (decompile DIR/x86.txt in the x86_64 program and DIR/arm.txt in the arm64 program with DecompileFunctions.java)
    python port/map/offset_vote_arch.py vote DIR

The two slices come from the same source but not every struct has the same layout (the resources object's file
system is at +0x160 on x86_64 and +0x148 on arm64). arm64 code builds large offsets from two instructions, so
constants in the features don't show them; Ghidra's decompiler puts them back together on both slices
(`*(int *)(param_1 + 0x154dc)`). For each host offset (port/mac_host/fm27_mac_x86_64.h), `select` picks up to
eight small matched x86_64 functions using it; `vote` reads both decompilations of every pair: an offset that
appears in both votes for itself, otherwise each arm64-only offset near it gets a share of the vote. Prints the
winner and its share per offset. Output stays local ($FM27_WORK_DIR).
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WINDOW = 0x400


def host_offsets():
    text = (ROOT / 'port/mac_host/fm27_mac_x86_64.h').read_text()
    out = {}
    for m in re.finditer(r'^\s+([a-z]+_\w+)\s+= (0x[0-9a-f]+),', text, re.M):
        if m.group(1).startswith(('fn_', 'g_', 'vt_', 'tlv_', 'seg_', 'image_', 'vslot_')): continue
        out[m.group(1)] = int(m.group(2), 16)
    return out


def select(args):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    pairs = {int(k): v for k, v in json.loads(Path(args.pairs).read_text()).items()}
    use = collections.defaultdict(list)
    insns = {}
    for line in open(args.x86):
        r = json.loads(line)
        if 'rva' not in r or r['rva'] not in pairs: continue
        insns[r['rva']] = r['insns']
        for v in set(r.get('disps', [])) | set(r['consts']): use[v].append(r['rva'])
    chosen = {}
    for name, off in host_offsets().items():
        if off < 0x10: continue
        fs = sorted(use.get(off, []), key=lambda f: insns[f])
        fs = [f for f in fs if insns[f] < 600][:8]
        for f in fs: chosen[f] = pairs[f]
        print(f'{name:22s} {off:#8x} {len(use.get(off, []))} users, {len(fs)} chosen')
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'pairs.json').write_text(json.dumps({hex(k): hex(v) for k, v in chosen.items()}))
    (out / 'x86.txt').write_text('\n'.join(hex(k) for k in chosen) + '\n')
    (out / 'arm.txt').write_text('\n'.join(hex(v) for v in chosen.values()) + '\n')
    print(len(chosen), 'pairs')


def offsets_in(path):
    if not path.is_file(): return None
    text = path.read_text(errors='replace')
    return {int(x, 16) for x in re.findall(r'\+ (0x[0-9a-f]+)\)', text)}


def vote(args):
    d = Path(args.dir)
    pairs = {int(k, 16): int(v, 16) for k, v in json.loads((d / 'pairs.json').read_text()).items()}
    xs = {f: offsets_in(next(iter(d.glob(f'x86dec/*_{f:x}.c')), Path('-'))) for f in pairs}
    ar = {a: offsets_in(next(iter(d.glob(f'armdec/*_{a:x}.c')), Path('-'))) for a in pairs.values()}
    result = {}
    for name, off in host_offsets().items():
        votes = collections.Counter(); n = 0
        for f, a in pairs.items():
            sx, sa = xs.get(f), ar.get(a)
            if not sx or not sa or off not in sx: continue
            n += 1
            if off in sa: votes[off] += 1; continue
            cands = [y for y in sa - sx if abs(y - off) <= WINDOW]
            for y in cands: votes[y] += 1 / len(cands)
        if not votes: print(f'{name:22s} {off:#8x}  no votes'); continue
        (best, k), *rest = votes.most_common(2) + [(None, 0)]
        result[name] = {'x86': hex(off), 'arm': hex(best), 'votes': round(k, 2), 'pairs': n, 'next': round(rest[0][1], 2)}
        flag = '' if best == off else '  CHANGED'
        print(f'{name:22s} {off:#8x} -> {best:#8x}  {k:.1f}/{n} (next {rest[0][1]:.1f}){flag}')
    (d / 'offsets.json').write_text(json.dumps(result, indent=1))


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('select'); s.add_argument('--x86'); s.add_argument('--arm'); s.add_argument('--pairs'); s.add_argument('--out')
    v = sub.add_parser('vote'); v.add_argument('dir')
    a = ap.parse_args()
    select(a) if a.cmd == 'select' else vote(a)


if __name__ == '__main__':
    main()
