# LockFrame Generator

**A consistency-first image-to-video generator. The first frame is the original image — pixel for pixel — and the character is never redrawn.**

Most AI video generators "animate" your image by repainting it. Faces drift, outfits change, props switch hands. LockFrame takes the opposite route:

1. **Cut, don't repaint.** The subject is segmented out of *your* image. Every pixel of the character in every frame comes from that cutout.
2. **Inpaint the stage.** The hole left behind is filled from the surrounding background, so the subject can actually move over its own scene.
3. **Animate the layers.** Walk-bob, sway, briefcase swing, fist pump and a closing nod are layer transforms (translate / rotate / scale) — never regeneration.
4. **Frame 0 is sacred.** The first output frame is the input image itself, byte-equivalent after resize. A built-in verifier checks this and the per-frame subject similarity, and fails the render if they drift.

Trade-off, stated plainly: motion is smaller than a diffusion generator's. The character bobs and steps in place-advance, it does not freely turn around. In exchange, it is *the same character* in every frame — same face, same stripes, same tie, same briefcase, in the same hand.

## Quick start

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python lockframe.py \
  --image input.jpg \
  --out output.mp4 \
  --duration 5 --fps 24 \
  --plan walk_and_nod
```

Plans: `walk` (forward bob + sway), `walk_and_nod` (walk, then a close push-in and one nod in the last second), `push_in` (subtle camera push only).

## Verify a render

```bash
.venv/bin/python verify.py --image input.jpg --video output.mp4
```

Prints frame-0 identity (must be exact) and subject-mask IoU across the clip.

## License

MIT
