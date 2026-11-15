"""VIDEO 02 — Bina EDL + data overlay untuk "NKT 3.mov".
(Disalin daripada edit/build_edl.py; hanya bahagian KONFIGURASI yang berbeza.)

Input : edit/v02/transkrip-NKT3.json
Output: edit/v02/edl.json, motion/overlay-data-v02.js

Semua masa dalam saat. Tukar senarai di bawah untuk ubah suntingan.
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
words = [w for s in json.load(open(ROOT / "edit/v02/transkrip-NKT3.json")) for w in s["words"]]

# Pembetulan ejaan subtitle (Whisper -> ejaan standard)
FIX = {"tak kala": "tatkala", "insyaAllah": "insya-Allah"}

# ---------------------------------------------------------------- 1. SEGMEN
# Jeda senyap (silencedetect -30dB, disahkan dengan tenaga audio; Whisper melebarkan masa perkataan).
# Jeda dramatik "tanpa ... pernah" (53.5–55.5) dikekalkan 0.6s. (12.85–13.51) dikecualikan (selamat).
SILENCES = [(4.15, 5.32), (7.35, 8.96), (10.06, 11.29), (14.18, 15.42), (15.63, 16.57), (17.88, 18.86),
            (19.95, 21.12), (21.86, 22.62), (23.33, 23.83), (24.64, 25.42), (27.26, 28.44), (30.78, 31.86),
            (34.28, 35.53), (36.89, 37.68), (38.49, 39.33), (41.00, 42.04), (43.21, 44.40), (46.22, 46.85),
            (48.53, 49.25), (51.40, 52.02), (53.53, 55.11), (56.15, 57.36), (57.61, 58.40), (59.84, 61.02),
            (61.91, 62.47), (63.02, 63.89), (64.21, 64.77), (65.00, 66.24)]
KEEP_PAD = 0.12

# Zoom per segmen: (zoom_mula, zoom_akhir). >1.0 = punch-in. Minimum 1.04 untuk buang
# jalur warna di siling kereta (atas frame).
COLD_OPEN = (61.00, 64.30)          # "Atas pilihan yang telah kita lakukan."
MAIN = (3.00, 67.10)

def main_segments():
    segs, cur = [], MAIN[0]
    for a, b in SILENCES:
        if a < cur or b > MAIN[1]:
            continue
        segs.append((cur, a + KEEP_PAD))
        cur = b - KEEP_PAD
    segs.append((cur, MAIN[1]))
    return segs

def zoom_for(src_in, idx):
    # Penutup emosi (kekuatan -> tanpa kesal -> percayalah): slow push-in
    if src_in >= 46.0:
        return (1.08, 1.18)
    return (1.04, 1.06) if idx % 2 == 0 else (1.12, 1.14)

FPS = 30
snap = lambda x: round(round(x * FPS) / FPS, 4)
edl, t = [], 0.0
edl.append(dict(src_in=snap(COLD_OPEN[0]), src_out=snap(COLD_OPEN[1]), out_in=0.0, zoom=(1.16, 1.28), tag="cold-open"))
t = edl[0]["src_out"] - edl[0]["src_in"]
for i, (a, b) in enumerate(main_segments()):
    a, b = snap(a), snap(b)
    edl.append(dict(src_in=a, src_out=b, out_in=round(t, 4), zoom=zoom_for(a, i), tag="main"))
    t += b - a
SPEECH_END = t

def to_out(src, prefer_cold=False):
    """Peta masa sumber -> masa output (segmen utama, kecuali prefer_cold)."""
    for s in edl:
        if prefer_cold != (s["tag"] == "cold-open"):
            continue
        if s["src_in"] - 1e-6 <= src <= s["src_out"] + 1e-6:
            return s["out_in"] + (src - s["src_in"])
    if prefer_cold:
        c = edl[0]
        return c["out_in"] + min(max(src, c["src_in"]), c["src_out"]) - c["src_in"]
    # jatuh dalam jeda yang dibuang -> ambil awal segmen seterusnya
    nxt = [s for s in edl if s["tag"] == "main" and s["src_in"] > src]
    return nxt[0]["out_in"] if nxt else SPEECH_END

# ---------------------------------------------------------------- 2. SUBTITLE
GOLD = {"perkahwinan", "proses", "memimpin", "keluarga", "bersyukur", "berbahagia", "menghormati", "menghargai",
        "bahagia", "islam", "agama", "kekuatan", "kekesalan", "pilihan", "percayalah", "isteri", "suami"}

def clean(w):
    return w.strip()

def chunk_captions(ws, prefer_cold=False, max_words=4, max_chars=24):
    caps, cur = [], []
    def flush():
        if cur:
            caps.append(dict(start=round(to_out(cur[0]["s"], prefer_cold), 3),
                             end=round(to_out(cur[-1]["e"], prefer_cold), 3),
                             words=[dict(w=clean(x["w"]), t=round(to_out(x["s"], prefer_cold), 3),
                                         gold=re.sub(r"[^a-z]", "", clean(x["w"]).lower()) in GOLD)
                                    for x in cur]))
            cur.clear()
    for w in ws:
        txt = " ".join(clean(x["w"]) for x in cur + [w])
        if cur and (len(cur) >= max_words or len(txt) > max_chars):
            flush()
        cur.append(w)
        if clean(w["w"]).endswith((".", ",", "?")):
            flush()
    flush()
    # "tak kala" -> "tatkala"
    for c in caps:
        ws2 = []
        for x in c["words"]:
            if ws2 and ws2[-1]["w"].lower() == "tak" and x["w"].lower().startswith("kala"):
                ws2[-1]["w"] = "tatkala" + x["w"][4:]
                continue
            if x["w"].startswith("insyaAllah"):
                x["w"] = x["w"].replace("insyaAllah", "insya-Allah")
            ws2.append(x)
        c["words"] = ws2
    # pastikan tiada pertindihan & tempoh minimum
    for i, c in enumerate(caps):
        nxt = caps[i + 1]["start"] if i + 1 < len(caps) else c["end"] + 0.6
        c["end"] = round(min(max(c["end"] + 0.15, c["start"] + 0.7), nxt), 3)
    return caps

main_words = [w for w in words if w["e"] > MAIN[0] + 0.2 and w["s"] < MAIN[1]]
cold_words = [w for w in words if w["e"] > COLD_OPEN[0] + 0.2 and w["e"] <= COLD_OPEN[1] + 0.25]
captions = chunk_captions(cold_words, prefer_cold=True, max_words=3) + chunk_captions(main_words)

# ---------------------------------------------------------------- 3. MOTION GRAPHICS
# Masa dalam SUMBER, dipetakan ke output. Jenis dikendalikan oleh motion/overlay.html
def ev(kind, src_a, src_b, **kw):
    return dict(kind=kind, start=round(to_out(src_a), 3), end=round(to_out(src_b), 3), **kw)

events = [
    dict(kind="hook", start=0.0, end=COLD_OPEN[1] - COLD_OPEN[0],
         lines=["KAHWIN TANPA KESAL", "ATAS", "PILIHAN KITA"]),
    ev("behind", 3.0, 9.0, kicker="PERKAHWINAN ADALAH SATU", word="PROSES", size=230,
       sub="", word_at=to_out(5.80)),
    ev("notif", 9.6, 30.6, tone="gold", app="PERKAHWINAN MENGAJAR KITA", items=[
        dict(label="PELAJARAN · 01", t="Cara memimpin keluarga", at=to_out(12.74), time="suami & isteri", icon="✓"),
        dict(label="PELAJARAN · 02", t="Erti bersyukur seadanya", at=to_out(25.80), time="sekarang", icon="✓"),
        dict(label="PELAJARAN · 03", t="Erti berbahagia cara kita", at=to_out(28.84), time="sekarang", icon="✓")]),
    ev("notif", 31.9, 43.3, tone="gold", app="PERKAHWINAN MEMBAWA KITA", items=[
        dict(label="PELAJARAN · 04", t="Menghormati & menghargai", at=to_out(35.53), time="sekarang", icon="✓"),
        dict(label="PELAJARAN · 05", t="Mencipta bahagia", at=to_out(39.33), time="sekarang", icon="✓")]),
    ev("check", 42.1, 46.1, text="✓ BAHAGIA BERLANDASKAN ACUAN ISLAM"),
    ev("flow", 46.3, 53.5, tone="good", title="AKHIRNYA", items=[
        dict(t="Diberi kekuatan", at=to_out(48.28)),
        dict(t="Teruskan kehidupan", at=to_out(49.60)),
        dict(t="Dalam alam perkahwinan", at=to_out(52.12))]),
    ev("behind", 53.5, 64.6, kicker="TANPA PERNAH MERASA", word="KESAL", size=270,
       sub="", word_at=to_out(58.40)),
    ev("check", 61.4, 64.6, text="✓ TIADA KESAL ATAS PILIHAN KITA"),
    ev("word", 66.1, 67.1, title="PERCAYALAH."),
]

data = dict(fps=30, speech_end=round(SPEECH_END, 3), cta_len=15.0, captions=captions, events=events)
(ROOT / "edit/v02/edl.json").write_text(json.dumps(dict(segments=edl, speech_end=SPEECH_END), indent=1))
(ROOT / "motion/overlay-data-v02.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
print(f"segmen: {len(edl)}  tempoh ucapan: {SPEECH_END:.2f}s  caption: {len(captions)}")
