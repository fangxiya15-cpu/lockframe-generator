"""Engine adapters for LockFrame v2.

One interface, many engines. A shot is always generated from the
full character kit + scene kit; adapters differ only in transport.
If an adapter fails a shot 4 rounds in a row, the pipeline moves
to the next adapter — the standard never drops.
"""

TIGHTEN = {
    # failed gate -> constraint appended to the next round's prompt
    "performance": "legs must alternate stepping visibly, no sliding, "
                   "no walking in place, weight shifts with each step",
    "consistency": "character must match the reference sheet exactly: "
                   "same face, same outfit, props stay in the locked hand, "
                   "no mirroring",
    "cinematography": "camera moves in one straight motivated path, "
                      "no orbiting, signage stays readable and undeformed",
    "finish": "no flicker, no extra limbs, no warped faces, clean fur detail",
    "scene": "background must match the scene kit exactly: same layout, "
             "same props in the same places, same light direction",
    "voice": "use only the locked voice id for this character, "
             "locked speed and pitch, no other voice",
}

class Adapter:
    name = "base"
    def generate(self, kit, shot, extra_constraints):
        raise NotImplementedError

class MediaToolAdapter(Adapter):
    name = "media"
    def generate(self, kit, shot, extra_constraints):
        """Reference-driven generation via the host's media tool:
        every reference image in the kit + the identity text
        verbatim + the shot description + tightened constraints."""
        prompt_images = kit["reference_images"] + \
            shot.get("extra_refs", [])
        prompt_text = " ".join([
            kit["identity_verbatim"], shot["description"],
            *extra_constraints])
        return {"images": prompt_images, "text": prompt_text,
                "dispatch": "media.generate_video"}

class KlingAdapter(Adapter):
    name = "kling"      # motion-control / character-consistency mode

class SeedanceAdapter(Adapter):
    name = "seedance"   # multi-reference mode

ADAPTER_ORDER = ["media", "kling", "seedance"]

def next_adapter(current):
    i = ADAPTER_ORDER.index(current)
    return ADAPTER_ORDER[i + 1] if i + 1 < len(ADAPTER_ORDER) else None
