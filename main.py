#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125.

Copies the pre-rendered front page (entry.png, drawn by draw_page.py
in this same repository) to the grader's output directory.

Standard library only; deterministic: the same bytes every run.
The output directory comes from MAKEFUN_OUTPUT_DIR, defaulting to
/output, exactly as the kit's RULES.txt describes.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(src):
        print("entry.png is missing next to main.py", file=sys.stderr)
        return 1
    shutil.copyfile(src, dst)
    # Confirm the copy is byte-identical to the shipped image.
    if sha256(src) != sha256(dst):
        print("copy mismatch: %s differs from %s" % (dst, src),
              file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
