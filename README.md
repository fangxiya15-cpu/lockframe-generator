# LockFrame Generator

**A Hongguo-benchmark image-to-video production pipeline: real performance *and* character consistency, enforced by a four-gate QC loop.**

## v2 architecture (current)

v1 proved a hard truth: a cutout that is never redrawn cannot drift — and cannot act. Sliding stickers do not pass a professional bar. v2 therefore inverts the design (see `pipeline.py` and `BENCHMARK.md`):

1. **Locked character kit** — turnaround, expressions, outfit and prop sheets built once from the user's reference; an identity description reused *verbatim* in every shot prompt; explicit left/right locks (a briefcase stays in the same paw).
2. **Reference-driven engines** — shots are really performed by a video generation engine behind an adapter, always fed the whole kit, never a single loose image.
3. **Four-gate QC per shot** — performance (legs really alternate, no sliding), consistency (same face / outfit / prop, same hand), cinematography (motivated camera, readable set signage), finish (resolution, no flicker, no extra limbs). Evidence frames are extracted per shot.
4. **Regenerate, never patch** — a failed gate re-shoots only that shot with the failed constraint tightened; 4 failed rounds switch the engine adapter. The standard never drops, and passed shots are assembled with designed transitions and per-shot audio padding so sync cannot drift.

The acceptance bar lives in [BENCHMARK.md](BENCHMARK.md) and is the project's constitution.

## v1 (legacy, `lockframe.py`)

**A consistency-first cutout animator. The first frame is the original image — pixel for pixel — and the character is never redrawn.** Kept for stills-like shots where pixel identity matters more than performance:

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
