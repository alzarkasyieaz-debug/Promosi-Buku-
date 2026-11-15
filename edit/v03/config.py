"""VIDEO 03 — NKT 4.mov | Hubungan dengan mertua (membalas komen penonton)."""
import json, pathlib
_H = pathlib.Path(__file__).parent
TRANSCRIPT = "edit/v03/transkrip.json"
SILENCES = [tuple(x) for x in json.load(open(_H / "silences.json"))]
# Nama penonton yang bertanya TIDAK dimasukkan: badan ucapan bermula pada "bertanyakan tentang..."
COLD_OPEN = (18.72, 21.78)        # "adalah ibu kita juga, adalah ayah kita juga"
MAIN = (7.15, 120.35)             # hingga "insya-Allah" (tanpa ucapan penutup yang menyebut nama)
BEHIND_TOP = 250
CLIMAX_FROM = 87.7
FIX = {"kabar": "khabar", "insyaAllah": "insya-Allah", "bersalah": "besar"}
GOLD = {"mertua", "ibu", "ayah", "bapa", "kasih", "sayang", "sama", "keutamaan", "pandangan", "pendapat",
        "khabar", "kabar", "telefon", "penting", "utama", "menghargai", "keputusan", "keluarga", "seimbangkan"}
HOOK_LINES = ["IBU & AYAH MERTUA", "ADALAH", "IBU BAPA KITA"]

def events(ev, T):
    return [
        ev("notif", 7.3, 17.9, tone="gold", app="MEMBALAS KOMEN PENONTON", items=[
            dict(label="SOALAN", t="Nasihat hubungan dengan mertua?", at=T(7.4), time="komen", icon="💬")]),
        ev("behind", 29.2, 37.0, kicker="HUBUNGAN & KEUTAMAAN", word="SAMA", size=280, sub="", word_at=T(31.11)),
        ev("check", 41.0, 47.8, text="✓ SAYANGI MERTUA SEPERTI IBU BAPA SENDIRI"),
        ev("notif", 51.6, 87.7, tone="gold", app="NASIHAT HUBUNGAN DENGAN MERTUA", items=[
            dict(label="NASIHAT · 01", t="Seimbangkan kasih sayang", at=T(53.59), time="pertama", icon="1"),
            dict(label="NASIHAT · 02", t="Kongsi pandangan, tanya pendapat", at=T(61.47), time="kedua", icon="2"),
            dict(label="NASIHAT · 03", t="Tanya khabar sekali-sekala", at=T(76.53), time="ketiga", icon="3")]),
        ev("behind", 88.4, 96.0, kicker="DAN YANG PALING", word="UTAMA", size=270, sub="", word_at=T(92.25)),
        ev("flow", 102.8, 116.0, tone="good", title="KONGSI SEBELUM BUAT KEPUTUSAN", items=[
            dict(t="Bercerita & kongsi pandangan", at=T(104.65)),
            dict(t="Mereka rasa penting", at=T(111.77)),
            dict(t="Mereka rasa dihargai", at=T(114.63))]),
        ev("check", 115.8, 119.2, text="✓ HARGAI PANDANGAN IBU BAPA MERTUA"),
        ev("word", 119.2, 120.35, title="INSYA-ALLAH."),
    ]
