#!/usr/bin/env python3
"""Map the host's x86_64 addresses to the arm64 slice of the same FM27 build (arm64 timing test).

    python port/map/match_arch.py --x86 FEATURES_X86.jsonl --arm FEATURES_ARM.jsonl \
        --header port/mac_host/fm27_mac_x86_64_2503222.h --arm-binary PATH/game_plugin_arm64 --out HEADER_ARM.h

Both feature files come from port/ghidra_scripts/ExportFunctionFeatures.java run on the two slices of one build (same
source, two compilers' back ends), so strings, call structure and most constants agree. Functions are matched with the
Windows->Mac matcher (match.Matcher: unique strings and constants, then call-graph propagation); data addresses
(globals, vtables, the thread-local descriptor) by votes from the matched functions that reference them. Segment
bounds come from the arm64 Mach-O load commands. Writes a header in the format of the x86_64 one (addresses and
evidence only; no game bytes) to a git-ignored or private path.
"""
import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from match import Matcher, load   # noqa: E402


def segments(binary):
    out = subprocess.run(['otool', '-l', str(binary)], capture_output=True, text=True, check=True).stdout
    segs = {}
    for block in out.split('Load command')[1:]:
        if 'cmd LC_SEGMENT_64' not in block: continue
        f = dict(t.split()[:2] for t in block.splitlines() if len(t.split()) >= 2)
        segs[f['segname']] = (int(f['vmaddr'], 16), int(f['vmaddr'], 16) + int(f['vmsize'], 16))
    return segs


def sections(binary):
    out = subprocess.run(['otool', '-l', str(binary)], capture_output=True, text=True, check=True).stdout
    secs = {}
    for block in out.split('Section')[1:]:
        f = dict(t.split()[:2] for t in block.splitlines() if len(t.split()) >= 2)
        if 'sectname' in f and 'addr' in f and 'size' in f: secs[f['sectname']] = (int(f['addr'], 16), int(f['addr'], 16) + int(f['size'], 16))
    return secs


def uuid_and_version(binary):
    out = subprocess.run(['dwarfdump', '--uuid', str(binary)], capture_output=True, text=True, check=True).stdout
    m = re.search(r'UUID: ([0-9A-F-]+) \(arm64\)', out)
    return m.group(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--x86', required=True); ap.add_argument('--arm', required=True)
    ap.add_argument('--header', required=True); ap.add_argument('--arm-binary', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    _, x86, _ = load(args.x86); _, arm, _ = load(args.arm)
    print(f'x86_64 functions {len(x86)}, arm64 functions {len(arm)}')
    mt = Matcher(x86, arm)
    print('string anchors:', mt.unique_feature_anchors('strings', 'string', min_len=6))
    print('const anchors:', mt.unique_feature_anchors('consts', 'const'))
    for r in range(3):
        print(f'propagation {r + 1}:', mt.propagate(rounds=12))
        print(f'string anchors again:', mt.unique_feature_anchors('strings', 'string', min_len=4))
    mt.similarity_evidence()
    print(f'matched {len(mt.w2m)}')

    # data: votes from matched functions referencing each x86 global
    refs_x = collections.defaultdict(list)
    for f, d in x86.items():
        for g in set(d['globals']): refs_x[g].append(f)
    refs_a = collections.defaultdict(set)
    for f, d in arm.items():
        for g in set(d['globals']): refs_a[g].add(f)

    def map_global(g):
        votes = collections.Counter(); n = 0
        for f in refs_x.get(g, []):
            a = mt.w2m.get(f)
            if a is None: continue
            n += 1
            for ga in set(arm[a]['globals']): votes[ga] += 1
        for t in [v for v in votes if any(lo <= v < hi for lo, hi in tls)]: del votes[t]   # thread-local descriptors ride along
        if not votes: return None, f'no matched referencer ({len(refs_x.get(g, []))} referencers)'
        (best, k), *rest = votes.most_common(2) + [(None, 0)]
        second = rest[0][1]
        # the arm64 global's own referencers should map back onto x86 referencers of g
        back = sum(1 for a in refs_a[best] if mt.m2w.get(a) in refs_x[g])
        ok = k >= 2 and k > second or (k == 1 and n == 1 and second == 0)
        return (best if ok else None), f'votes {k}/{n} (next {second}), back {back}/{len(refs_a[best])}'

    segs = segments(args.arm_binary)
    tls = [(lo, hi) for name, (lo, hi) in sections(args.arm_binary).items() if name.startswith('__thread')]
    lines = Path(args.header).read_text().splitlines()
    out, missing = [], []
    for line in lines:
        m = re.match(r'#define FM27_RVA_(\w+) (0x[0-9a-f]+)', line)
        if not m: continue
        name, x = m.group(1), int(m.group(2), 16)
        if name.startswith('fn_'):
            a = mt.w2m.get(x)
            if a is None:
                missing.append(name); out.append(f'#define FM27_RVA_{name} 0x0   // UNMAPPED (x86_64 {x:#x})'); continue
            ev = sorted(mt.evidence[(x, a)] - {'size'})
            out.append(f'#define FM27_RVA_{name} {a:#x}   // x86_64 {x:#x}; {",".join(ev) or "size only"}')
        elif name == 'seg_data_const_begin':
            out.append(f'#define FM27_RVA_{name} {segs["__DATA_CONST"][0]:#x}')
        elif name == 'seg_data_const_end':
            out.append(f'#define FM27_RVA_{name} {segs["__DATA_CONST"][1]:#x}')
        elif name == 'image_text_end':
            out.append(f'#define FM27_RVA_{name} {segs["__TEXT"][1]:#x}')
        else:
            a, why = map_global(x)
            if a is None:
                missing.append(name); out.append(f'#define FM27_RVA_{name} 0x0   // UNMAPPED (x86_64 {x:#x}; {why})'); continue
            out.append(f'#define FM27_RVA_{name} {a:#x}   // x86_64 {x:#x}; {why}')
    uuid = uuid_and_version(args.arm_binary).replace('-', '')
    head = [f'// FM27 macOS game_plugin arm64 slice (LC_UUID {uuid_and_version(args.arm_binary)}).',
            '// Generated by port/map/match_arch.py from the x86_64 header of the same build. Addresses and evidence only.',
            '#pragma once', '#define FM27_RVA(name, value) FM27_RVA_##name',
            '#define FM27_MAC_UUID ' + ','.join(f'0x{uuid[i:i + 2]}' for i in range(0, 32, 2))]
    for line in lines:
        if line.startswith('#define FM27_MAC_ENGINE_VERSION') or line.startswith('#define FM27_MAC_GAME_VERSION'): head.append(line)
    Path(args.out).write_text('\n'.join(head + out) + '\n')
    print(f'wrote {args.out}; unmapped: {missing or "none"}')


if __name__ == '__main__':
    main()
