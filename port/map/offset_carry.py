"""Carry struct field offsets from one FM27 Mac build to the next (x86_64 slices, local files only).

When a game update grows a record (27.1 added bytes to the player record), every field after the insertion moves.
Functions that touch those fields compile to the same instructions with different displacements. This script:
1. disassembles every function in an address range of both slices and keys each one by its instruction pattern
   (mnemonics and registers; displacements, immediates and branch targets ignored);
2. pairs old and new functions whose key is unique in both builds (the same code, possibly with moved fields);
3. aligns each pair instruction by instruction and records, per base register context, old displacement -> new
   displacement for memory operands (not rip, rsp or rbp);
4. prints, for each offset asked for (or every offset seen), the votes: e.g. 0xc9b -> 0x1233 x214.
Struct types aren't known, so an offset used by two record types can have split votes; the votes show it.

  python port/map/offset_carry.py OLD_SLICE NEW_SLICE [--lo 0x4900000 --hi 0x5300000] [--offsets 0xc9b,0xcd8 | --header H]
      [--json OUT.json]

Nothing derived from game bytes is written to the repository; write --json output to $FM27_WORK_DIR.
"""
import argparse, collections, json, re, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, x86

sys.path.insert(0, str(Path(__file__).resolve().parent))
from update_rvas import Image

SKIP_BASE = (0, x86.X86_REG_RIP, x86.X86_REG_RSP, x86.X86_REG_RBP)


def functions(img, lo, hi):
    md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
    starts = sorted(a for a in img.fset if lo <= a < hi)
    out = {}
    for a in starts:
        n = img.flen(a)
        if not n or n > 400000: continue
        ins = list(img.insns(a, n))
        key = []
        mem = []
        for i in ins:
            regs = []
            for op in i.operands:
                if op.type == x86.X86_OP_REG: regs.append(op.reg)
                elif op.type == x86.X86_OP_MEM: regs.append(('m', op.mem.base, op.mem.index, op.mem.scale, op.size))
                elif op.type == x86.X86_OP_IMM: regs.append('i')
            key.append((i.mnemonic, tuple(regs)))
            mem.append(next(((op.mem.base, op.mem.disp) for op in i.operands if op.type == x86.X86_OP_MEM and op.mem.base not in SKIP_BASE), None))
        out[a] = (hash(tuple(key)), mem)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('old'); p.add_argument('new')
    p.add_argument('--lo', default='0x4900000'); p.add_argument('--hi', default='0x5300000')
    p.add_argument('--offsets', help='comma-separated offsets to report'); p.add_argument('--json')
    a = p.parse_args(); lo, hi = int(a.lo, 16), int(a.hi, 16)
    old, new = Image(a.old), Image(a.new)
    fo, fn = functions(old, lo, hi), functions(new, lo, hi)
    by = lambda f: collections.Counter(k for k, _ in f.values())
    co, cn = by(fo), by(fn)
    idx_new = {k: addr for addr, (k, _) in fn.items() if cn[k] == 1}
    pairs = [(ao, idx_new[k]) for ao, (k, _) in fo.items() if co[k] == 1 and k in idx_new]
    votes = collections.defaultdict(collections.Counter)
    moved_pairs = 0
    for ao, an in pairs:
        mo, mn = fo[ao][1], fn[an][1]
        moved = False
        for x, y in zip(mo, mn):
            if x and y:
                votes[x[1]][y[1]] += 1
                moved |= x[1] != y[1]
        moved_pairs += moved
    print(f'functions: old {len(fo)}, new {len(fn)}; paired {len(pairs)}, of which {moved_pairs} with moved displacements', file=sys.stderr)
    want = [int(x, 16) for x in a.offsets.split(',')] if a.offsets else sorted(votes)
    report = {}
    for off in want:
        v = votes.get(off)
        report[hex(off)] = {hex(k): c for k, c in v.most_common(4)} if v else {}
        if a.offsets: print(hex(off), report[hex(off)])
    if a.json: Path(a.json).write_text(json.dumps(report, indent=0))


if __name__ == '__main__':
    main()
