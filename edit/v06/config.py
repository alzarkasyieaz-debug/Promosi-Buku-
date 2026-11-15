"""VIDEO 06 — NKT 7.mov | Pasangan ialah hadiah Allah: ada kekurangan, baiki bersama."""
import json, pathlib
_H = pathlib.Path(__file__).parent
TRANSCRIPT = "edit/v06/transkrip.json"
# Rakaman luar (bising): silencedetect -23dB selepas high-pass 120Hz
SILENCES = [tuple(x) for x in json.load(open(_H / "silences.json"))]
COLD_OPEN = (52.50, 58.55)        # "Ada kekurangan? Baiki bersama. Ada kelebihan? Rasai bersama."
MAIN = (1.50, 69.15)
CLIMAX_FROM = 46.6
FIX = {"insyaAllah": "insya-Allah", "InsyaAllah": "Insya-Allah"}
# "Ta 'ala" -> "Taala"; "Ada -ada" (gagap) -> "Ada"; tanda soal -> noktah pada "bersama"
WORD_FIX = {2.3: "Taala", 2.6: None, 41.54: "Taala", 41.8: None, 63.92: "Taala", 64.16: None,
            52.6: "Ada", 55.64: "Ada", 54.98: "bersama.", 57.96: "bersama."}
GOLD = {"pasangan", "hadiahkan", "melengkapkan", "kelemahan", "kekurangan", "kekhilafan", "tanggungjawab",
        "membetulkan", "menasihati", "nasihat", "memperingati", "diberkati", "allah", "baiki", "rasai",
        "bersama", "kelebihan", "bahagia", "percayalah", "taala", "swt", "hayat"}
HOOK_LINES = ["ADA KEKURANGAN? BAIKI BERSAMA.", "ADA KELEBIHAN?", "RASAI BERSAMA."]

def events(ev, T):
    return [
        ev("behind", 1.6, 6.3, kicker="PASANGAN ITU", word="HADIAH", size=270, sub="", word_at=T(2.76)),
        ev("notif", 6.3, 13.2, tone="gold", app="PASANGAN HADIR UNTUK", items=[
            dict(label="HIKMAH · 01", t="Melengkapkan kelemahan kita", at=T(6.54), time="hadiah", icon="✓"),
            dict(label="HIKMAH · 02", t="Dia juga ada kekurangan", at=T(11.68), time="manusia", icon="✓")]),
        ev("flow", 13.26, 24.4, tone="good", title="TANGGUNGJAWAB KITA", items=[
            dict(t="Membetulkan", at=T(18.26)),
            dict(t="Menasihati", at=T(20.10)),
            dict(t="Tak terus dalam kekhilafan", at=T(21.82))]),
        ev("notif", 24.42, 31.5, tone="gold", app="SEBAGAI PASANGAN", items=[
            dict(label="ADA KALANYA", t="Kita menerima nasihat", at=T(28.50), time="↓", icon="✓"),
            dict(label="ADA KALANYA", t="Kita memberi nasihat", at=T(30.74), time="↑", icon="✓")]),
        ev("behind", 31.6, 40.4, kicker="SALING", word="MEMPERINGATI", size=200, sub="", word_at=T(32.48)),
        ev("check", 35.6, 40.4, text="✓ PROSES MENGENALI SEPANJANG HAYAT"),
        ev("flow", 40.48, 52.4, tone="good", title="ALLAH BERIKAN DIA KEPADA KITA", items=[
            dict(t="Bukan sekadar lengkapkan hidup", at=T(44.62)),
            dict(t="Membawa ke arah jalan", at=T(47.72)),
            dict(t="Yang diberkati Allah SWT", at=T(50.26))]),
        ev("notif", 52.6, 58.5, tone="gold", app="BERSAMA-SAMA", items=[
            dict(label="ADA KEKURANGAN?", t="Baiki bersama", at=T(54.42), time="−", icon="−"),
            dict(label="ADA KELEBIHAN?", t="Rasai bersama", at=T(57.30), time="+", icon="+")]),
        ev("check", 59.4, 67.8, text="✓ BAHAGIA BERSAMA HINGGA AKHIR HAYAT"),
        ev("word", 67.92, 69.15, title="PERCAYALAH."),
    ]
