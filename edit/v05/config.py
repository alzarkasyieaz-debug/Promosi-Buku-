"""VIDEO 05 — NKT 6.mov | Menasihati pasangan yang kurang menjaga solat (membalas soalan)."""
import json, pathlib
_H = pathlib.Path(__file__).parent
TRANSCRIPT = "edit/v05/transkrip.json"
SILENCES = [tuple(x) for x in json.load(open(_H / "silences.json"))]
# Nama penanya TIDAK dimasukkan: mula pada "bertanya bagaimana...", tamat pada "Dan insya-Allah."
COLD_OPEN = (33.86, 39.40)        # "jangan menghukum, tetapi menasihati dengan cara yang paling lembut"
MAIN = (5.50, 87.50)
BEHIND_TOP = 250
CLIMAX_FROM = 66.3
FIX = {"insyaAllah": "insya-Allah"}
# Pembetulan ikut masa (semak manual): "Ta 'ala" -> "Taala"; "dia uji sebut," -> "diuji, sebut,"
WORD_FIX = {78.06: "Taala", 78.32: None, 75.46: "diuji,", 75.56: None}
GOLD = {"solat", "berjemaah", "jemaah", "imamkan", "menghukum", "menasihati", "lembut", "hikmah", "doakan",
        "hati", "allah", "taala", "tegur", "cakna", "memelihara", "rindunya", "penting", "pasangan"}
HOOK_LINES = ["JANGAN MENGHUKUM", "TETAPI NASIHATI", "DENGAN LEMBUT"]

def events(ev, T):
    return [
        ev("notif", 5.6, 12.9, tone="gold", app="MEMBALAS SOALAN PENONTON", items=[
            dict(label="SOALAN", t="Pasangan kurang jaga solat?", at=T(5.7), time="soalan", icon="💬")]),
        ev("behind", 13.18, 19.9, kicker="CARA PERTAMA · AJAK SOLAT", word="BERJEMAAH", size=200, sub="", word_at=T(15.66)),
        ev("notif", 20.1, 30.0, tone="gold", app="AJAK SOLAT BERSAMA", items=[
            dict(label="CARA · 01", t="Minta pasangan imamkan kita", at=T(22.32), time="jemaah", icon="1"),
            dict(label="CARA · 01", t="Ajak isteri solat bersama", at=T(26.18), time="jemaah", icon="1")]),
        ev("behind", 30.1, 41.4, kicker="CARA KEDUA · JANGAN MENGHUKUM", word="LEMBUT", size=270, sub="", word_at=T(37.26)),
        ev("notif", 41.5, 47.1, tone="gold", app="CONTOH UNGKAPAN", items=[
            dict(label="UNGKAPAN", t="Dah lama tak solat jemaah sekali", at=T(42.18), time="💬", icon="2"),
            dict(label="UNGKAPAN", t="Rindunya nak solat sekali", at=T(44.72), time="💬", icon="2")]),
        ev("check", 47.2, 54.1, text="✓ AJAK DENGAN PENUH HIKMAH"),
        ev("behind", 54.2, 66.2, kicker="CARA KETIGA", word="DOAKAN", size=270, sub="", word_at=T(60.10)),
        ev("check", 62.7, 66.3, text="✓ MOGA TERBUKA HATI JAGA SOLAT"),
        ev("flow", 66.34, 86.5, tone="bad", title="CARA KEEMPAT · BILA DIUJI", items=[
            dict(t="Ujian dalam keluarga", at=T(71.06)),
            dict(t="Mungkin teguran Allah", at=T(78.70)),
            dict(t="Kurang memelihara solat", at=T(81.76))]),
        ev("word", 86.58, 87.5, title="INSYA-ALLAH."),
    ]
