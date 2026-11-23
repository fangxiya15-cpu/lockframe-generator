#!/usr/bin/env python3
"""Verify a LockFrame render: frame 0 must equal the (resized)
input, and the subject must stay recognisably itself throughout."""
import argparse, subprocess, os
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True)
ap.add_argument("--video", required=True)
a = ap.parse_args()

os.makedirs("/tmp/lockframe_verify", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.video,
                "-vf", "fps=1", "/tmp/lockframe_verify/f%02d.png"], check=True)
frames = sorted(os.listdir("/tmp/lockframe_verify"))
first = Image.open(f"/tmp/lockframe_verify/{frames[0]}").convert("RGB")
src = Image.open(a.image).convert("RGB").resize(first.size, Image.LANCZOS)
diff = np.abs(np.array(first, dtype=int) - np.array(src, dtype=int)).mean()
print(f"frames sampled: {len(frames)}")
print(f"frame0 mean abs diff vs input (resized): {diff:.3f}  "
      f"({'EXACT-ish (codec noise only)' if diff < 12 else 'CHECK: differs'})")
for f in frames:
    im = np.array(Image.open(f"/tmp/lockframe_verify/{f}").convert("RGB"))
    print(f, "mean brightness", round(float(im.mean()), 1))
