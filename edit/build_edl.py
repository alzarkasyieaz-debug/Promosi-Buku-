"""Bina Edit Decision List (EDL) + data overlay untuk video NKT.mov.

Input : edit/transkrip-NKT.json (Whisper large-v3, masa perkataan)
Output: edit/edl.json            (segmen sumber -> output, zoom)
        motion/overlay-data.js   (subtitle + motion graphics dalam masa OUTPUT)

Semua masa dalam saat. Tukar senarai di bawah untuk ubah suntingan.
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
words = [w for s in json.load(open(ROOT / "edit/transkrip-NKT.json")) for w in s["words"]]

# Pembetulan ejaan subtitle (Whisper -> ejaan standard)
FIX = {"tak kala": "tatkala", "insyaAllah": "insya-Allah"}

# ---------------------------------------------------------------- 1. SEGMEN
# Jeda senyap (ffmpeg silencedetect -35dB, >0.45s) dipendekkan kepada ~0.2s.
SILENCES = [(3.52, 4.15), (9.09, 9.64), (14.16, 14.74), (17.10, 17.77), (22.95, 23.45),
            (39.00, 39.47), (57.85, 58.31), (70.12, 70.94), (72.08, 73.39), (76.30, 77.06),
            (81.95, 82.99), (84.17, 85.03)]
KEEP_PAD = 0.10

# Zoom per segmen: (zoom_mula, zoom_akhir). >1.0 = punch-in. Minimum 1.04 untuk buang
# jalur warna di siling kereta (atas frame).
COLD_OPEN = (85.95, 89.12)          # "...boleh runtuhnya institusi. Institusi kekeluargaan"
MAIN = (1.65, 94.35)

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
    # Emotional climax (76s+) : slow cinematic push-in
    if src_in >= 76.0:
        return (1.10, 1.22)
    # Nasihat utama (47–57s): push-in perlahan
    if 47.0 <= src_in < 57.8:
        return (1.06, 1.14)
    # Lain-lain: selang-seli wide / punch-in pada setiap potongan (sembunyi jump cut)
    return (1.04, 1.06) if idx % 2 == 0 else (1.13, 1.15)

FPS = 30
snap = lambda x: round(round(x * FPS) / FPS, 4)
edl, t = [], 0.0
edl.append(dict(src_in=snap(COLD_OPEN[0]), src_out=snap(COLD_OPEN[1]), out_in=0.0, zoom=(1.18, 1.30), tag="cold-open"))
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
GOLD = {"ujian", "cabaran", "kesediaan", "persiapan", "emosi", "melatah", "keputusan",
        "tindakan", "runtuhnya", "institusi", "kekeluargaan", "percayalah", "asam", "garam", "takut"}

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

main_words = [w for w in words if MAIN[0] <= w["s"] < MAIN[1]]
cold_words = [w for w in words if COLD_OPEN[0] <= w["s"] and w["e"] <= COLD_OPEN[1] + 0.05]
captions = chunk_captions(cold_words, prefer_cold=True, max_words=3) + chunk_captions(main_words)

# ---------------------------------------------------------------- 3. MOTION GRAPHICS
# Masa dalam SUMBER, dipetakan ke output. Jenis dikendalikan oleh motion/overlay.html
def ev(kind, src_a, src_b, **kw):
    return dict(kind=kind, start=round(to_out(src_a), 3), end=round(to_out(src_b), 3), **kw)

events = [
    dict(kind="hook", start=0.0, end=COLD_OPEN[1] - COLD_OPEN[0],
         lines=["EMOSI YANG TAK TERKAWAL", "BOLEH MERUNTUHKAN", "RUMAH TANGGA"]),
    # Kata besar DI BELAKANG penceramah (text-behind-subject, gaya rujukan "audience")
    ev("behind", 1.80, 12.9, kicker="UJIAN & CABARAN ITU", word="ASAM GARAM", size=124,
       sub="dalam pernikahan", word_at=to_out(10.59)),
    # Tindanan kad notifikasi (gaya rujukan notifikasi iOS) untuk point tersusun
    ev("notif", 18.20, 28.9, tone="gold", app="YANG PERLU KITA RISAU", items=[
        dict(label="PERSEDIAAN · 01", t="Bagaimana kesediaan kita", at=to_out(21.09), time="sekarang", icon="✓"),
        dict(label="PERSEDIAAN · 02", t="Bagaimana persiapan kita", at=to_out(23.87), time="sekarang", icon="✓")]),
    ev("notif", 36.9, 47.3, tone="red", app="AGAR KITA TIDAK", items=[
        dict(label="ELAK · 01", t="Melatah", at=to_out(38.15), time="!", icon="✕"),
        dict(label="ELAK · 02", t="Buat keputusan terburu-buru", at=to_out(40.61), time="!", icon="✕"),
        dict(label="ELAK · 03", t="Merugikan pasangan & diri sendiri", at=to_out(43.25), time="!", icon="✕")]),
    ev("behind", 49.8, 57.7, kicker="PERSEDIAAN PENGURUSAN", word="EMOSI", size=270,
       sub="sebelum melangkah ke alam perkahwinan", word_at=to_out(52.21)),
    # Pill ✓ bercahaya (gaya rujukan) — ganti lower third seketika
    ev("check", 55.4, 57.9, text="✓ URUS EMOSI SEBELUM KAHWIN"),
    ev("flow", 61.2, 76.0, tone="good", title="BILA EMOSI TERURUS", items=[
        dict(t="Urus emosi dengan baik", at=to_out(63.89)),
        dict(t="Keputusan yang baik", at=to_out(74.07)),
        dict(t="Tindakan yang baik", at=to_out(75.03))]),
    ev("flow", 78.3, 93.2, tone="bad", title="BILA EMOSI TAK TERKAWAL", items=[
        dict(t="Gagal mengawal emosi", at=to_out(79.79)),
        dict(t="Implikasi berpanjangan", at=to_out(81.85)),
        dict(t="Runtuhnya institusi kekeluargaan", at=to_out(86.39))]),
    ev("check", 74.1, 76.4, text="✓ EMOSI TERURUS, KEPUTUSAN PUN BAIK"),
    ev("word", 93.35, 94.35, title="PERCAYALAH."),
]

data = dict(fps=30, speech_end=round(SPEECH_END, 3), cta_len=15.0, captions=captions, events=events)
(ROOT / "edit/edl.json").write_text(json.dumps(dict(segments=edl, speech_end=SPEECH_END), indent=1))
(ROOT / "motion/overlay-data.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
print(f"segmen: {len(edl)}  tempoh ucapan: {SPEECH_END:.2f}s  caption: {len(captions)}")
