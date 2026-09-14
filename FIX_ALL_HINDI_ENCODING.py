from pathlib import Path
import re

FILES = [
    Path('index.html'),
    Path('app.js'),
    Path('srdm-readable-print-final.js'),
    Path('srdm-readable-print-final.css'),
]

# Common Windows-1252 mojibake characters created when UTF-8 text is decoded incorrectly.
SUSPECT_MARKERS = ('à¤','à¥','â€','â€¢','â€”','â€“','â†','âœ','â˜','Ã','Â','ðŸ')
TOKEN_RE = re.compile(r"[^\x00-\x7F]+")

CP1252_EXTRA = {chr(i) for i in range(0x80,0x100)} | set('€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ')

def suspicious_score(s: str) -> int:
    return sum(s.count(m) for m in SUSPECT_MARKERS)

def try_fix_piece(piece: str) -> str:
    if suspicious_score(piece) == 0:
        return piece
    best = piece
    best_score = suspicious_score(piece)
    cur = piece
    for _ in range(3):
        try:
            candidate = cur.encode('cp1252').decode('utf-8')
        except Exception:
            try:
                candidate = cur.encode('latin1').decode('utf-8')
            except Exception:
                break
        score = suspicious_score(candidate)
        # Accept if it reduces mojibake markers or yields Devanagari.
        if score < best_score or any('\u0900' <= ch <= '\u097f' for ch in candidate):
            best, best_score = candidate, score
            cur = candidate
        else:
            break
    return best

def repair_text(text: str) -> tuple[str,int]:
    changes = 0
    def repl(m):
        nonlocal changes
        old = m.group(0)
        new = try_fix_piece(old)
        if new != old:
            changes += 1
        return new
    # Repair only non-ASCII runs, leaving valid ASCII/HTML/JS untouched.
    out = TOKEN_RE.sub(repl, text)
    return out, changes

def main():
    total_changes = 0
    changed_files = []
    for p in FILES:
        if not p.exists():
            continue
        raw = p.read_text(encoding='utf-8-sig')
        fixed, n = repair_text(raw)
        if n:
            p.write_text(fixed, encoding='utf-8', newline='')
            changed_files.append((str(p), n))
            total_changes += n
    print('HINDI ENCODING REPAIR COMPLETE')
    for name, n in changed_files:
        print(f'  {name}: repaired {n} mojibake text runs')
    print(f'TOTAL repaired runs: {total_changes}')

if __name__ == '__main__':
    main()
