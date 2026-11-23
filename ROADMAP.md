# Optimization roadmap

Done in v2.1:
- [x] Measurable QC (`qc.py`): resolution/fps gate, flicker score,
      lower-body motion energy (catches sliding cutouts numerically)
- [x] Engine adapters (`adapters.py`) with per-gate constraint
      tightening and a fail-over order — 4 failed rounds switch engine
- [x] Scene + voice gates, multi-cast division table (v2.0)

Next, in priority order:
1. **Face-identity embedding score** — cosine similarity between
   per-frame face crops and the kit's face sheet (InsightFace),
   turning the consistency gate from vision-scored to measured.
2. **Voice fingerprint check** — speaker-embedding similarity of
   each line against the character's locked voice reference;
   auto-reject lines below threshold instead of manual pitch checks.
3. **Prop-side detector** — locate the locked prop (e.g. briefcase)
   per frame and verify it never crosses the screen midline.
4. **Scene-layout matching** — feature-point match of backgrounds
   against the scene kit; flag moved furniture / duplicated signage.
5. **Cost & time ledger per shot** — rounds, engine, spend per passed
   shot, so a series budget is visible before it is blown.
6. **Parallel shot queue** — independent shots generate + QC in
   parallel; assembly waits for the full passed set.
7. **Regression corpus** — every failed shot is archived with its
   gate verdicts; adapter or prompt changes must re-run the corpus
   before shipping (a change that fixes one shot and breaks three
   others never lands).
