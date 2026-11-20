"""Which engine functions take a hidden return slot on arm64 (x8)? (arm64 timing test)

    python port/map/arm64_sret_check.py GAME_PLUGIN_ARM64 0xRVA [0xRVA ...]

On x86_64 the hidden return slot is the first argument (rdi), so a host call with an output pointer first works for
both kinds of function there. On arm64 it is passed in x8. This disassembles the first instructions of each function
(llvm-objdump, read-only) and reports whether x8 is read before anything writes it, which is what a function
returning through the slot does. Prints the instructions it based that on.
"""
import re
import subprocess
import sys

NO_DEST = re.compile(r'^(str|stp|stur|st1|cmp|cmn|tst|cbz|cbnz|tbz|tbnz|b\.|b$|bl$|blr|br|ret|ccmp|prfm)')


def regs(text):
    return set(re.findall(r'\b([xw]\d+|sp|xzr|wzr|lr|fp)\b', text))


def check(binary, rva, count=48):
    out = subprocess.run(['xcrun', 'llvm-objdump', '-d', '--no-show-raw-insn', f'--start-address={rva:#x}',
                          f'--stop-address={rva + 4 * count:#x}', binary], capture_output=True, text=True).stdout
    lines = [l for l in out.splitlines() if re.match(r'\s+[0-9a-f]+:', l)]
    written, seen = set(), []
    for l in lines:
        ins = l.split(':', 1)[1].strip().split(';')[0].strip()
        parts = ins.split(None, 1)
        mnem, ops = parts[0], (parts[1] if len(parts) > 1 else '')
        seen.append(ins)
        operands = [o.strip() for o in re.split(r',(?![^\[]*\])', ops)]
        if NO_DEST.match(mnem): dest, srcs = set(), regs(ops)
        elif mnem.startswith('ldp'): dest, srcs = regs(','.join(operands[:2])), regs(','.join(operands[2:]))
        else: dest, srcs = regs(operands[0]) if operands else set(), regs(','.join(operands[1:]))
        if ('x8' in srcs or 'w8' in srcs) and 'x8' not in written: return True, seen
        if 'x8' in dest or 'w8' in dest: written.add('x8')
        if mnem in ('bl', 'blr', 'b', 'br', 'ret'): break
    return False, seen


def main():
    binary = sys.argv[1]
    for a in sys.argv[2:]:
        rva = int(a, 16)
        uses, seen = check(binary, rva)
        print(f'{rva:#x}: {"HIDDEN RETURN (x8)" if uses else "no x8 slot"}')
        for ins in seen[:14]: print('    ', ins)


if __name__ == '__main__':
    main()
