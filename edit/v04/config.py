"""VIDEO 04 — NKT 5.mov | 3 ucapan yang sangat mahal dalam hubungan keluarga (membalas komen)."""
import json, pathlib
_H = pathlib.Path(__file__).parent
TRANSCRIPT = "edit/v04/transkrip.json"
SILENCES = [tuple(x) for x in json.load(open(_H / "silences.json"))]
# Nama penonton TIDAK dimasukkan: mula pada "Antara ucapan terbaik...", tamat pada "insya-Allah".
COLD_OPEN = (11.86, 15.62)        # "ada tiga perkara ataupun tiga ucapan yang sangat mahal"
MAIN = (7.62, 98.72)
BEHIND_TOP = 250
CLIMAX_FROM = 75.0
# Pembetulan Whisper (semak manual): "sumpah"->"sedap", "setiap kelas hati"->"dengan ikhlas hati"
FIX = {"sumpah": "sedap", "kelas": "ikhlas", "setiap": "dengan", "insyaAllah": "insya-Allah"}
GOLD = {"ucapan", "terima", "kasih", "minta", "tolong", "maaf", "kemaafan", "mahal", "menghargai", "arahan",
        "ikhlas", "membantu", "kekhilafan", "perbalahan", "pudar", "hubungan", "keluarga", "kekeluargaan", "tiga"}
HOOK_LINES = ["ADA 3 UCAPAN", "YANG SANGAT", "MAHAL"]

def events(ev, T):
    return [
        ev("notif", 7.7, 11.6, tone="gold", app="MEMBALAS KOMEN PENONTON", items=[
            dict(label="SOALAN", t="Ucapan terbaik dalam keluarga?", at=T(7.75), time="komen", icon="💬")]),
        ev("behind", 19.1, 26.6, kicker="UCAPAN PERTAMA", word="TERIMA KASIH", size=170, sub="", word_at=T(20.86)),
        ev("check", 23.9, 26.6, text="✓ TANDA KITA MENGHARGAI"),
        ev("notif", 26.62, 32.7, tone="gold", app="UNTUK SEMUA AHLI KELUARGA", items=[
            dict(label="KELUARGA", t="Suami & isteri", at=T(27.18), time="❤", icon="✓"),
            dict(label="KELUARGA", t="Anak-anak", at=T(28.88), time="❤", icon="✓"),
            dict(label="KELUARGA", t="Ibu & ayah", at=T(30.02), time="❤", icon="✓")]),
        ev("behind", 32.72, 37.1, kicker="UCAPAN KEDUA", word="MINTA TOLONG", size=170, sub="", word_at=T(34.84)),
        ev("flow", 37.2, 46.4, tone="good", title="LEBIH BAIK DARIPADA ARAHAN", items=[
            dict(t="Ayah kepada anak", at=T(41.26)),
            dict(t="Suami kepada isteri", at=T(43.30)),
            dict(t="Isteri kepada suami", at=T(44.42))]),
        ev("check", 55.6, 60.4, text="✓ DIBUAT DENGAN NIAT MEMBANTU"),
        ev("behind", 62.66, 68.0, kicker="UCAPAN KETIGA", word="MAAF", size=290, sub="", word_at=T(66.66)),
        ev("check", 79.2, 83.3, text="✓ AKUI KEKHILAFAN"),
        ev("flow", 80.74, 90.2, tone="bad", title="BILA KITA MEMPERTAHANKAN", items=[
            dict(t="Tak mahu mengaku salah", at=T(82.28)),
            dict(t="Perbalahan berpanjangan", at=T(84.44)),
            dict(t="Hubungan semakin pudar", at=T(89.66))]),
        ev("check", 91.2, 97.9, text="✓ MOHON MAAF, BAIKI HUBUNGAN"),
        ev("word", 97.9, 98.72, title="INSYA-ALLAH."),
    ]
