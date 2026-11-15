"""Pustaka EDL dikongsi untuk video 03 dan seterusnya.

Setiap video mempunyai edit/vNN/config.py yang mentakrifkan:
  TRANSCRIPT  : laluan transkrip Whisper (relatif kepada akar repo)
  SILENCES    : senarai (mula, tamat) jeda senyap dalam masa SUMBER
  COLD_OPEN   : (mula, tamat) klip hook
  MAIN        : (mula, tamat) badan ucapan
  CLIMAX_FROM : masa sumber; segmen selepas ini diberi slow push-in
  GOLD        : set kata kunci subtitle berwarna emas
  HOOK_LINES  : 3 baris teks hook
  def events(ev, T): senarai event motion graphics (masa SUMBER; T() peta ke OUTPUT)

Guna: python3 edit/edl_lib.py v03
Output: edit/vNN/edl.json, motion/overlay-data-vNN.js
"""
import json, re, sys, pathlib, importlib.util

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 30
KEEP_PAD = 0.12
snap = lambda x: round(round(x * FPS) / FPS, 4)


def load_config(vid):
    p = ROOT / "edit" / vid / "config.py"
    spec = importlib.util.spec_from_file_location(f"cfg_{vid}", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def build(vid):
    C = load_config(vid)
    words = [w for s in json.load(open(ROOT / C.TRANSCRIPT)) for w in s["words"]]

    # ---- segmen
    segs, cur = [], C.MAIN[0]
    for a, b in sorted(C.SILENCES):
        if a < cur or b > C.MAIN[1]:
            continue
        segs.append((cur, a + KEEP_PAD)); cur = b - KEEP_PAD
    segs.append((cur, C.MAIN[1]))

    def zoom_for(a, i):
        if a >= C.CLIMAX_FROM:
            return (1.08, 1.18)
        return (1.04, 1.06) if i % 2 == 0 else (1.12, 1.14)

    edl = [dict(src_in=snap(C.COLD_OPEN[0]), src_out=snap(C.COLD_OPEN[1]), out_in=0.0, zoom=(1.16, 1.28), tag="cold-open")]
    t = edl[0]["src_out"] - edl[0]["src_in"]
    for i, (a, b) in enumerate(segs):
        a, b = snap(a), snap(b)
        if b - a < 0.2:
            continue
        edl.append(dict(src_in=a, src_out=b, out_in=round(t, 4), zoom=zoom_for(a, i), tag="main")); t += b - a
    speech_end = t

    def to_out(src, cold=False):
        if cold:
            c = edl[0]; return c["out_in"] + min(max(src, c["src_in"]), c["src_out"]) - c["src_in"]
        for s in edl[1:]:
            if s["src_in"] - 1e-6 <= src <= s["src_out"] + 1e-6:
                return s["out_in"] + (src - s["src_in"])
        nxt = [s for s in edl[1:] if s["src_in"] > src]
        return nxt[0]["out_in"] if nxt else speech_end

    # ---- subtitle
    def captions_for(ws, cold, max_words=4, max_chars=24):
        caps, cur = [], []
        def flush():
            if cur:
                caps.append(dict(start=round(to_out(cur[0]["s"], cold), 3), end=round(to_out(cur[-1]["e"], cold), 3),
                                 words=[dict(w=x["w"].strip(), t=round(to_out(x["s"], cold), 3),
                                             gold=re.sub(r"[^a-z]", "", x["w"].strip().lower()) in C.GOLD) for x in cur]))
                cur.clear()
        for w in ws:
            txt = " ".join(x["w"].strip() for x in cur + [w])
            if cur and (len(cur) >= max_words or len(txt) > max_chars):
                flush()
            cur.append(w)
            if w["w"].strip().endswith((".", ",", "?", "!")):
                flush()
        flush()
        for c in caps:
            for x in c["words"]:
                for a, b in getattr(C, "FIX", {}).items():
                    x["w"] = x["w"].replace(a, b)
        for i, c in enumerate(caps):
            nxt = caps[i + 1]["start"] if i + 1 < len(caps) else c["end"] + 0.6
            c["end"] = round(min(max(c["end"] + 0.15, c["start"] + 0.7), nxt), 3)
        return caps

    cold_w = [w for w in words if w["e"] > C.COLD_OPEN[0] + 0.2 and w["e"] <= C.COLD_OPEN[1] + 0.25]
    main_w = [w for w in words if w["e"] > C.MAIN[0] + 0.2 and w["s"] < C.MAIN[1]]
    cold_caps = captions_for(cold_w, True, max_words=3)
    main_caps = captions_for(main_w, False)
    if cold_caps and main_caps:
        cold_caps[-1]["end"] = min(cold_caps[-1]["end"], main_caps[0]["start"])
    captions = cold_caps + main_caps

    # ---- motion graphics
    def ev(kind, a, b, **kw):
        return dict(kind=kind, start=round(to_out(a), 3), end=round(to_out(b), 3), **kw)
    events = [dict(kind="hook", start=0.0, end=round(edl[0]["src_out"] - edl[0]["src_in"], 3), lines=C.HOOK_LINES)]
    events += C.events(ev, to_out)

    data = dict(fps=FPS, speech_end=round(speech_end, 3), cta_len=19.2, captions=captions, events=events)
    (ROOT / "edit" / vid / "edl.json").write_text(json.dumps(dict(segments=edl, speech_end=speech_end), indent=1))
    (ROOT / "motion" / f"overlay-data-{vid}.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    print(f"{vid}: segmen {len(edl)}  ucapan {speech_end:.2f}s  caption {len(captions)}")
    return data


if __name__ == "__main__":
    build(sys.argv[1])
