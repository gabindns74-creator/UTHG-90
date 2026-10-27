"""Récupère les séances et le bien-être depuis intervals.icu (synchro Garmin gratuite).

Clé lue dans INTERVALS_API_KEY (secret GitHub), jamais écrite dans le repo.
Sorties : seances/activites.csv, seances/bien-etre.csv, seances/resume.md
Pas de trace GPS ni de lieu : le repo est public.
"""
import base64, csv, datetime as dt, json, os, sys, urllib.request
from collections import defaultdict

OLDEST = "2025-07-01"
API = "https://intervals.icu/api/v1/athlete/0"

def get(path, **params):
    key = os.environ["INTERVALS_API_KEY"].strip()
    q = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(f"{API}/{path}?{q}")
    req.add_header("Authorization", "Basic " + base64.b64encode(f"API_KEY:{key}".encode()).decode())
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def pace(m, s):
    if not m or not s: return ""
    p = s / (m / 1000)
    return f"{int(p // 60)}:{int(p % 60):02d}"

def hms(s):
    s = int(s or 0)
    return f"{s // 3600}:{s % 3600 // 60:02d}"

def num(v, nd=0):
    return "" if v in (None, "") else round(v, nd) if nd else int(round(v))

ACT = ["date", "heure", "sport", "nom", "km", "duree", "allure_min_km", "d_plus_m",
       "fc_moy", "fc_max", "charge", "rpe", "ressenti", "calories", "notes"]

def activites(newest):
    rows = []
    for a in get("activities", oldest=OLDEST, newest=newest):
        if a.get("_note") or not a.get("start_date_local"):
            continue  # activités venues de Strava : l'API ne les expose pas
        d, _, h = a["start_date_local"].partition("T")
        dist, mt = a.get("distance") or 0, a.get("moving_time") or 0
        run = "Run" in (a.get("type") or "")
        rows.append({
            "date": d, "heure": h[:5], "sport": a.get("type", ""), "nom": a.get("name", ""),
            "km": num(dist / 1000, 2) if dist else "", "duree": hms(mt),
            "allure_min_km": pace(dist, mt) if run else "",
            "d_plus_m": num(a.get("total_elevation_gain")),
            "fc_moy": num(a.get("average_heartrate")), "fc_max": num(a.get("max_heartrate")),
            "charge": num(a.get("icu_training_load")), "rpe": a.get("icu_rpe") or "",
            "ressenti": a.get("feel") or "", "calories": num(a.get("calories")),
            "notes": (a.get("description") or "").replace("\n", " ")[:300],
        })
    rows.sort(key=lambda r: (r["date"], r["heure"]))
    return rows

BE = ["date", "fc_repos", "hrv", "sommeil_h", "poids", "fatigue", "courbatures", "forme_ctl", "fatigue_atl"]

def bien_etre(newest):
    rows = []
    for w in get("wellness", oldest=OLDEST, newest=newest):
        rows.append({
            "date": w.get("id", ""), "fc_repos": num(w.get("restingHR")), "hrv": num(w.get("hrv")),
            "sommeil_h": num((w.get("sleepSecs") or 0) / 3600, 1) or "", "poids": num(w.get("weight"), 1),
            "fatigue": w.get("fatigue") or "", "courbatures": w.get("soreness") or "",
            "forme_ctl": num(w.get("ctl")), "fatigue_atl": num(w.get("atl")),
        })
    return sorted(rows, key=lambda r: r["date"])

def resume(rows):
    sem = defaultdict(lambda: defaultdict(float))
    for r in rows:
        d = dt.date.fromisoformat(r["date"])
        s = sem[d - dt.timedelta(days=d.weekday())]
        h, m = r["duree"].split(":")
        t = int(h) * 60 + int(m)
        sport = r["sport"]
        if "Run" in sport:
            s["course_km"] += float(r["km"] or 0); s["course_dplus"] += float(r["d_plus_m"] or 0)
            s["course_n"] += 1
            if t >= 120: s["longues"] += 1
        elif "Ride" in sport:
            s["velo_min"] += t
        elif sport in ("WeightTraining", "Workout"):
            s["renfo_n"] += 1
        else:
            s["autre_min"] += t
        s["charge"] += float(r["charge"] or 0)
    out = ["# Résumé hebdomadaire", "",
           "Généré par `sync_seances.py` depuis intervals.icu. Semaine = lundi.", "",
           "| Semaine | Course | km | D+ | Sorties ≥ 2h | Vélo | Renfo | Autre | Charge |",
           "|---|---|---|---|---|---|---|---|---|"]
    for w in sorted(sem, reverse=True):
        s = sem[w]
        out.append(f"| {w} | {int(s['course_n'])} | {s['course_km']:.1f} | {int(s['course_dplus'])} | "
                   f"{int(s['longues'])} | {hms(s['velo_min'] * 60)} | {int(s['renfo_n'])} | "
                   f"{hms(s['autre_min'] * 60)} | {int(s['charge'])} |")
    return "\n".join(out) + "\n"

def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    if not os.environ.get("INTERVALS_API_KEY"):
        sys.exit("INTERVALS_API_KEY manquant (secret GitHub du repo)")
    newest = (dt.date.today() + dt.timedelta(days=1)).isoformat()
    os.makedirs("seances", exist_ok=True)
    acts = activites(newest)
    write_csv("seances/activites.csv", ACT, acts)
    write_csv("seances/bien-etre.csv", BE, bien_etre(newest))
    with open("seances/resume.md", "w", encoding="utf-8") as f:
        f.write(resume(acts))
    print(f"{len(acts)} activités")
