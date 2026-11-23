#!/usr/bin/env python3
"""LockFrame: consistency-first image-to-video.

Frame 0 == input image. The subject is segmented once (rembg),
the background is inpainted once (OpenCV), and every frame after
that is a layer transform of those original pixels. Nothing is
ever regenerated, so the character cannot drift, mirror, or
switch props between hands.
"""
import argparse, math, os, subprocess, sys
import numpy as np
from PIL import Image

def segment(rgba_img):
    """Return (subject_rgba, alpha_mask_np). Uses rembg (u2net);
    the model sees the image once, at t=0, and never again.
    Segmentation runs at reduced width (512px) and the alpha is
    upscaled — full-res inference OOMs on small machines and the
    mask does not need pixel-level resolution."""
    from rembg import remove, new_session
    w, h = rgba_img.size
    small = rgba_img.resize((512, round(h * 512 / w)), Image.LANCZOS)
    out_small = remove(small, session=new_session("u2net"))
    alpha_small = np.array(out_small)[:, :, 3]
    alpha_img = Image.fromarray(alpha_small).resize((w, h), Image.LANCZOS)
    alpha = np.array(alpha_img)
    out = rgba_img.copy()
    out.putalpha(alpha_img)
    return out, alpha

def inpaint_background(img_rgb, alpha):
    import cv2
    bgr = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    mask = (alpha > 10).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((15, 15), np.uint8))
    filled = cv2.inpaint(bgr, mask, 12, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(filled, cv2.COLOR_BGR2RGB))

def ease(t):
    return t * t * (3 - 2 * t)

def render(image_path, out_path, duration=5, fps=24, plan="walk_and_nod",
           width=704, height=1248):
    src = Image.open(image_path).convert("RGB")
    # Cover-crop to target aspect, centred — this resized image IS frame 0.
    scale = max(width / src.width, height / src.height)
    base = src.resize((round(src.width * scale), round(src.height * scale)),
                      Image.LANCZOS)
    x = (base.width - width) // 2; y = (base.height - height) // 2
    base = base.crop((x, y, x + width, y + height))

    subject, alpha = segment(base.convert("RGBA"))
    background = inpaint_background(base, alpha)

    n = int(duration * fps)
    frames_dir = out_path + ".frames"
    os.makedirs(frames_dir, exist_ok=True)

    for i in range(n):
        t = i / max(n - 1, 1)          # 0..1 over the clip
        sec = t * duration
        if i == 0:
            frame = base.copy()        # sacred: frame 0 is the original
        else:
            # Walk cycle: bob twice per second, gentle sway.
            bob = -abs(math.sin(sec * math.pi * 2)) * 10
            sway = math.sin(sec * math.pi * 2) * 1.2  # degrees
            grow = 1.0 + 0.05 * ease(min(t / 0.8, 1.0))  # stepping closer
            nod = 0.0
            if plan == "walk_and_nod" and sec > duration - 1.0:
                k = (sec - (duration - 1.0))  # 0..1 in the last second
                grow += 0.13 * ease(k)                    # push to close-up
                nod = math.sin(k * math.pi) * 3.0         # one nod, degrees
            layer = subject.resize(
                (round(width * grow), round(height * grow)), Image.LANCZOS)
            layer = layer.rotate(sway + nod, resample=Image.BICUBIC,
                                 center=(layer.width // 2, layer.height // 3))
            bg = background.resize(layer.size, Image.LANCZOS)
            canvas = bg.copy()
            canvas.paste(layer, (0, round(bob * grow)), layer)
            frame = canvas.crop(((canvas.width - width) // 2,
                                 (canvas.height - height) // 2,
                                 (canvas.width + width) // 2,
                                 (canvas.height + height) // 2))
        frame.save(f"{frames_dir}/{i:04d}.png")

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", f"{frames_dir}/%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", out_path], check=True)
    print(f"wrote {out_path} ({n} frames, frame0=original)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=5)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--plan", default="walk_and_nod",
                    choices=["walk", "walk_and_nod", "push_in"])
    a = ap.parse_args()
    render(a.image, a.out, a.duration, a.fps, a.plan)
