import datetime as dt, sys
start = dt.date(2026,10,26)
D = lambda w,d: start + dt.timedelta(weeks=w-1, days=d)

RULES = ("Règles de flexibilité : tu peux permuter les jours dans la semaine, tant que (1) jamais 2 séances dures d'affilée, "
         "(2) pas de renfo la veille de la sortie longue, (3) le vélo peut toujours remplacer une course facile si le pied ou les jambes tirent.")
PAIN = "Si le pied (bord externe) se réveille : pas de course ce jour-là, vélo à la place."
RAIN_RUN = "Plan B météo (pluie, verglas, nuit) : tapis de course en salle, ou inverse avec la séance vélo/renfo d'un autre jour."
RAIN_BIKE = "Plan B météo : home trainer ou vélo de salle même durée. Sinon elliptique, ou natation."
RENFO = {1:"Renfo niveau 1 (~30 min) : mollets 3x15 sur 2 pieds, squat 3x15, step-down 3x8/jambe, pont fessier 3x15, gainage 3x30s, élastique éversion cheville 3x15, short foot + 1 pied 3x30s.",
         2:"Renfo niveau 2 (~35 min) : mollets 3x12 sur 1 pied, squat bulgare 3x10/jambe, step-down 3x12, pont 1 jambe 3x12, nordic curl assisté 3x5, gainage 3x45s, élastique 3x20, équilibre yeux fermés.",
         3:"Renfo niveau 3 (~40 min) : mollets 1 pied lesté descente lente 3x12, bulgare lesté 3x8 (+ squat sauté 3x6 dès mars), step-down lesté 3x12, pont pieds surélevés 3x12, nordic 3x6-8, gainage 3x1min, élastique dur 3x20, équilibre sur coussin."}
RENFO_B = "Renfo B (~30 min, peut se faire après le vélo) : gainage planche, latéral et superman 3x40s, fentes marchées 3x10/jambe, chaise 3x45s, mollets excentriques sur une marche 3x12, élastique cheville 4 directions 3x15, équilibre 1 pied 3x45s, pompes 3x10."
NUTRI = "Sortie > 2h : teste ta stratégie anti-crampes (500-1000 mg sodium/h, 500-750 ml/h, 60-90 g glucides/h). Note ce que tu prends et si crampes."

# Allures (min/km), calées sur l'historique Garmin (10 km en 44:08, FC max ~198)
REPRISE = "5:45-6:00"   # 2 premières semaines
EF      = "5:30-5:50"   # footing, FC < 150
RECUP   = "5:50-6:10"   # lendemain de sortie longue
LONGUE  = "5:40-6:00"   # sortie longue sur route / chemins
AM      = "5:00-5:10"   # allure marathon, FC 155-163
SEUIL   = "4:35-4:45"   # FC 165-175
VMA_C   = "4:00-4:10"   # 400 à 1200 m
VMA_L   = "4:15-4:25"   # 1500 à 2000 m
COURT   = "3:45-3:55"   # 30/30, 1'/1'
COTE    = "5:00-5:30"   # montée à Fourvière (8-10 %), effort 8/10
TRAIL   = "6:00-6:30 sur le plat, marche active dans les montées raides (600-800 m D+/h), descentes relâchées"

def mins(km, pace=5.7): return int(round(km*pace/5)*5)
def dplus(v):
    if not v: return ""
    lo = max(int(round(v*0.85/50)*50), 50)
    hi = max(int(round(v*1.15/50)*50), lo+50)
    return f" · D+ {lo}-{hi} m"

def dtxt(v): return dplus(v)[len(" · D+ "):]

ev = []
def add(day, title, desc): ev.append((day, title, desc))
def renfo(day, lvl, extra=""): add(day, f"💪 Renfo N{lvl}", RENFO[lvl] + (" " + extra if extra else ""))
def velo(day, dur, extra=""):
    add(day, f"🚴 Vélo {dur} · FC 130-150", f"Vélo endurance {dur}, FC 130-150, tu dois pouvoir discuter. {extra}\n{RAIN_BIKE}")
def repos(day, extra="Repos complet, ou marche / mobilité 20 min."): add(day, "😴 Repos", extra)
def dim_samoens(day, dp="400-700"):
    add(day, f"🥾 Rando ou raquettes 1h30-2h · D+ {dp} m", f"Par défaut tu es à Samoëns, sans vélo jusqu'au printemps : rando ou raquettes à allure facile (FC < 145), D+ {dp} m.\nSi tu restes à Lyon : vélo 1h30 FC 130-150 (home trainer s'il pleut), ou repos si fatigué.")
def run(day, title, desc, long=False):
    d = desc + "\n" + PAIN + "\n" + RAIN_RUN
    if long: d += "\n" + NUTRI
    add(day, "🏃 " + title, d)
def footing(day, km, pace=EF, dp=0, extra=""):
    t = mins(km)
    run(day, f"Footing {km} km ({t}') · {pace}/km{dplus(dp)}",
        f"{km} km, environ {t} min, à {pace}/km sur le plat, FC sous 150." + (f" D+ visé : {dtxt(dp)} (dans les montées, garde la FC sous 155 et laisse filer l'allure)." if dp else "") + (" " + extra if extra else ""))
def frac(day, title, corps, pace, km_total, head=""):
    effort, _, rec = corps.partition(", ")
    run(day, f"{title} @ {pace}/km",
        (head + "\n" if head else "") + f"15' échauffement à {EF}/km + 3 lignes droites, puis {effort} à {pace}/km" + (f", {rec} en trottinant à 6:30-7:00/km" if rec else "") + f", puis 10' retour au calme à {EF}/km.\nTotal ~{km_total} km. Lieu : plat (berges du Rhône, parc de la Tête d'Or) ou piste. Pluie : tapis.")

# Phase 0 : reprise
for w in (1,2):
    renfo(D(w,0),1)
    if w==1:
        for d in (1,3,5): run(D(w,d), f"Footing 25' · {REPRISE}/km", f"25' à {REPRISE}/km sur plat, sol souple, FC sous 145. Tu dois pouvoir parler en phrases complètes.")
    else:
        run(D(w,1), f"Footing 30' · {REPRISE}/km", f"30' à {REPRISE}/km, plat, FC sous 145.")
        run(D(w,3), f"Footing 30' · {REPRISE}/km", f"30' à {REPRISE}/km, plat, FC sous 145.")
        run(D(w,5), f"Footing 40' · {REPRISE}/km", f"40' à {REPRISE}/km, plat. Si aucune gêne le lendemain, tu passes en phase 1.")
    velo(D(w,2),"1h-1h30")
    add(D(w,2),"💪 Renfo B",RENFO_B)
    renfo(D(w,4),1)
    dim_samoens(D(w,6), "300-500")

# Phase 1 : base. semaine -> (km, D+ semaine, allégée)
p1={3:(22,0,False),4:(26,0,False),5:(30,200,False),6:(22,100,True),
    7:(32,300,False),8:(36,400,False),9:(40,600,False),10:(30,300,True)}
P1F={5:("Fractionné 10 x 30/30","10 x 30\" rapide / 30\" trot",COURT,8),
     7:("Fractionné 12 x 30/30","12 x 30\" rapide / 30\" trot",COURT,8),
     8:("Fractionné 2 x 8 x 30/30","2 séries de 8 x 30\" rapide / 30\" trot (3' trot entre séries)",COURT,9),
     9:("Fractionné 8 x 1'/1'","8 x 1' rapide / 1' trot",COURT,10)}
for w,(km,dp,light) in p1.items():
    lvl = 1 if w<5 else 2
    lk=round(km*0.35); tk=round(km*0.25); hk=round(km*0.25); sk=km-lk-tk-hk
    if sk<5: lk+=sk; sk=0
    head=f"Semaine S{w}"+(" (allégée)" if light else "")+f" : ~{km} km" + (f", ~{dp} m D+ au total." if dp else ".")
    renfo(D(w,0),lvl)
    if w in P1F:
        t,c,p,k = P1F[w]; frac(D(w,1), t, c, p, k, head)
    else:
        footing(D(w,1), tk, extra=head + " Finis par 4 lignes droites de 80 m.")
    velo(D(w,2),"1h30-2h")
    add(D(w,2),"💪 Renfo B",RENFO_B)
    if w>=5 and not light:
        reps = 6 if w==5 else 8
        run(D(w,3), f"Côtes {reps} x 1' · montée {COTE}/km{dplus(max(dp*0.25,120))}",
            f"{hk} km au total. 15' échauffement à {EF}/km, puis {reps} x 1' en montée à Fourvière (Choulans ou Gourguillon) à {COTE}/km, effort 8/10, descente en trottinant à 6:30/km. 10' retour au calme.")
    else:
        footing(D(w,3), hk)
    renfo(D(w,4),lvl,"Ou repos si la semaine est chargée.")
    run(D(w,5), f"Sortie longue {lk} km ({mins(lk,5.83)}') · {LONGUE}/km{dplus(dp*0.6)}",
        f"{lk} km à {LONGUE}/km, FC sous 150. Samoëns : chemins de vallée (Giffre) ou raquettes. Lyon : parcs, berges, Fourvière." + (f" D+ visé : {dtxt(dp*0.6)}." if dp else ""))
    if sk: footing(D(w,6), sk, RECUP, extra="Récupération, sur plat. À Samoëns : rando 1h30 possible à la place.")
    else: dim_samoens(D(w,6))

# Phases 2 et 3 : (semaine, km, D+, durée longue, qualité jeudi, libellé, renfo, allégée)
weeks = [
 (11,40,1000,"1h45","CA","Développement A",2,False),
 (12,44,1200,"2h","CA","Développement A",2,False),
 (13,48,1400,"2h15","CA","Développement A",2,False),
 (14,34,800,"1h30",None,"Développement A (allégée)",2,True),
 (15,48,1400,"2h15","S","Développement B",3,False),
 (16,52,1600,"2h30","S","Développement B",3,False),
 (17,55,1800,"2h45","S","Développement B",3,False),
 (18,40,1000,"2h",None,"Développement B (allégée)",3,True),
 (19,55,1800,"2h45","CL","Développement C",3,False),
 (20,58,2000,"3h","CL","Développement C",3,False),
 (21,60,2200,"3h15","CL","Développement C",3,False),
 (22,45,1200,"2h15",None,"Développement C (allégée)",3,True),
 (23,55,2200,"3h","SPE","Spécifique D",3,False),
 (24,60,2600,"3h30","SPE","Spécifique D",3,False),
 (25,65,3000,"4h","SPE","Spécifique D",3,False),
 (26,45,1500,"2h30",None,"Spécifique D (allégée)",3,True),
 (27,62,2800,"4h","SPE","Spécifique E",3,False),
 (28,None,None,None,None,"Course de prépa",3,True),
 (29,50,2000,"3h",None,"Spécifique E (reprise après course)",3,True),
 (30,70,4000,"5-6h","SPE","Spécifique E (semaine choc)",3,False),
 (31,50,2500,"3h","S","Affûtage -30%",3,False),
 (32,38,1500,"2h30",None,"Affûtage -45%",3,True),
 (33,25,800,None,None,"Affûtage -60% / semaine de course",3,True),
]
TUE={11:("Fractionné 10 x 400 m","10 x 400 m, récup 1'",VMA_C,9),12:("Fractionné 6 x 800 m","6 x 800 m, récup 1'30",VMA_C,10),
     13:("Fractionné 5 x 1000 m","5 x 1000 m, récup 2'",VMA_C,10),15:("Fractionné 6 x 1000 m","6 x 1000 m, récup 1'30",VMA_C,11),
     16:("Fractionné 4 x 1500 m","4 x 1500 m, récup 2'",VMA_L,11),17:("Fractionné 3 x 2000 m","3 x 2000 m, récup 2'30",VMA_L,11),
     19:("Fractionné 6 x 1000 m","6 x 1000 m, récup 1'30",VMA_C,11),20:("Fractionné 5 x 1200 m","5 x 1200 m, récup 1'30",VMA_C,11),
     21:("Fractionné 4 x 2000 m","4 x 2000 m, récup 2'",VMA_L,13),31:("Fractionné 6 x 1000 m","6 x 1000 m, récup 1'30",VMA_C,11)}
THU_S={15:"3 x 8'",16:"3 x 8'",17:"3 x 10'",31:"2 x 10'"}
THU_T={23:("Seuil 2 x 15'",SEUIL,"2 x 15', récup 3'"),24:("Seuil 3 x 12'",SEUIL,"3 x 12', récup 2'"),
       25:("Tempo 40' vallonné",AM,"40' en continu sur parcours vallonné"),27:("Seuil 3 x 10'",SEUIL,"3 x 10', récup 2'"),
       30:("Tempo 30'",AM,"30' en continu")}
for (w,km,dp,ld,q,lab,lvl,light) in weeks:
    head = f"{lab}, semaine S{w}" + (f" : ~{km} km, ~{dp} m D+ au total." if km else ".")
    if w==28:
        renfo(D(w,0),3,"Version légère : 2 séries au lieu de 3.")
        footing(D(w,1), 7, extra=head + " Finis par 4 lignes droites.")
        velo(D(w,2),"1h","Très facile.")
        footing(D(w,3), 5)
        repos(D(w,4),"Repos, prépare ton matériel et ta nutrition de course.")
        run(D(w,5),"COURSE DE PRÉPA (40-60 km) – à choisir", f"Course de préparation, à placer ce week-end (samedi ou dimanche). Répétition générale : 1re moitié très facile ({TRAIL}), FC sous 150 dans les montées, nutrition, sel, matériel.", long=True)
        repos(D(w,6),"Repos ou marche. Si la course est dimanche, inverse avec samedi.")
        continue
    if w==33:
        renfo(D(w,0),3,"Version très légère, pas de charges lourdes.")
        run(D(w,1), f"Footing 40' · {EF}/km + 3 x 3' @ {AM}/km", head + f" 40' à {EF}/km avec 3 x 3' à {AM}/km pour réveiller les jambes.")
        velo(D(w,2),"45'","Très facile.")
        run(D(w,3), f"Footing 30' · {RECUP}/km", f"30' à {RECUP}/km, jambes légères.")
        repos(D(w,4),"Repos. À ajuster quand la date exacte de l'UTHG 90 est connue.")
        add(D(w,5),"🏔️ UTHG 90 km (date à confirmer)","Semaine de course. Déplace cet événement à la vraie date de l'UTHG 2027. Objectif réaliste 13:30-14:30/km de moyenne tout compris. Départ facile, FC sous 150 dans les montées, tu marches toutes les montées raides, sel + glucides dès la 1re heure.")
        repos(D(w,6),"Récupération.")
        continue
    renfo(D(w,0),lvl)
    # Mardi
    if light:
        frac(D(w,1), "Fractionné 8 x 30/30", "8 x 30\" rapide / 30\" trot", COURT, 8, head)
    elif w in TUE:
        t,c,p,k = TUE[w]; frac(D(w,1), t, c, p, k, head)
    else:
        v = dp*0.15
        run(D(w,1), f"Côtes spécifiques 4 x 6'{dplus(v)}",
            head + f"\n15' échauffement à {EF}/km, puis 4 x 6' en montée (Fourvière, ou tapis à 12-15 %) en alternant course à {COTE}/km et marche rapide avec bâtons, FC 160-170. Descentes courues à 5:15-5:45/km pour travailler les quadris. 10' retour au calme. D+ visé : {dtxt(v)}.")
    # Mercredi
    if w < 23:
        velo(D(w,2),"1h30-2h","Si fatigue, tu peux le remplacer par du repos.")
        if not light: add(D(w,2),"💪 Renfo B",RENFO_B)
    else:
        velo(D(w,2),"1h30","Ou 45' de course à "+EF+"/km si le vélo n'est pas dispo.")
    # Jeudi
    tk = round(km*0.22)
    if light or q is None:
        footing(D(w,3), tk, dp=dp*0.15)
    elif q=="CA":
        run(D(w,3), f"Côtes 8 x 1'30 · montée {COTE}/km{dplus(dp*0.2)}", f"15' échauffement à {EF}/km, 8 x 1'30 en montée à Fourvière à {COTE}/km (effort 8/10), descente en trottinant. 10' retour au calme. D+ visé : {dtxt(dp*0.2)}.\nSi tu es fatigué après mardi : footing {tk} km à {EF}/km à la place.")
    elif q=="CL":
        run(D(w,3), f"Côtes longues 4 x 5' · montée {COTE}/km{dplus(dp*0.2)}", f"15' échauffement à {EF}/km, 4 x 5' en montée (Choulans / Gourguillon ou tapis 10-15 %) à {COTE}/km, redescente en courant à 5:15-5:45/km pour les quadris. 10' retour au calme. D+ visé : {dtxt(dp*0.2)}.")
    elif w in THU_T:
        t,p,c = THU_T[w]; frac(D(w,3), t, c, p, 11)
    else:
        frac(D(w,3), f"Seuil {THU_S[w]}", f"{THU_S[w]}, récup 2'", SEUIL, 10)
    renfo(D(w,4),lvl,"Ou repos. Jamais la veille d'une grosse sortie longue : si besoin déplace-le au jeudi.")
    # Samedi : sortie longue
    lk = round(km*0.40); lv = dp*0.55
    run(D(w,5), f"Sortie longue {ld} (~{lk} km) · plat 6:00-6:30/km{dplus(lv)}",
        f"{ld}, ~{lk} km, D+ visé : {dtxt(lv)}.\nAllure : {TRAIL}. FC sous 150 (155 max dans les montées).\nSamoëns : sentiers ou raquettes / ski de rando si neige. Lyon : boucles Fourvière (Choulans, Gourguillon, Chazeaux) ou tapis incliné, et sur le plat {LONGUE}/km.", long=True)
    # Dimanche
    sk = max(km - tk - lk - round(km*0.2), round(km*0.18))
    sv = dp*0.15
    if w>=23 and not light:
        run(D(w,6), f"Enchaînement {sk} km · {RECUP}/km{dplus(sv)}", f"Lendemain de sortie longue : {sk} km sur jambes fatiguées à {RECUP}/km sur le plat, D+ visé : {dtxt(sv)}, FC sous 145. Idéal en montagne à Samoëns.")
    else:
        footing(D(w,6), sk, RECUP, sv, "Récupération. Ou rando / raquettes 1h30 à Samoëns.")

# Ajustements météo (Meteoblue Lyon), mis à jour par Claude dans ajustements.json :
# {"meteo": {"AAAA-MM-JJ": "texte prévision"}, "echanges": [["AAAA-MM-JJ", "AAAA-MM-JJ", "raison"]]}
import json, os
_aj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajustements.json")
AJ = json.load(open(_aj)) if os.path.exists(_aj) else {}
for a_, b_, why in AJ.get("echanges", []):
    a_, b_ = dt.date.fromisoformat(a_), dt.date.fromisoformat(b_)
    for i_, (day, t, d) in enumerate(ev):
        if day == a_: ev[i_] = (b_, t + " 🔁", d + f"\nDéplacé du {a_:%d/%m} : {why}")
        elif day == b_: ev[i_] = (a_, t + " 🔁", d + f"\nDéplacé du {b_:%d/%m} : {why}")
for i_, (day, t, d) in enumerate(ev):
    m_ = AJ.get("meteo", {}).get(day.isoformat())
    if m_: ev[i_] = (day, t, f"Météo Lyon (Meteoblue) : {m_}\n\n" + d)

def esc(s): return s.replace("\\","\\\\").replace(";",r"\;").replace(",","\\,").replace("\n","\\n")
def fold(line):
    b = line.encode(); out=[]
    while len(b)>75:
        cut=75
        while (b[cut] & 0xC0)==0x80: cut-=1
        out.append(b[:cut]); b=b" "+b[cut:]
    out.append(b); return b"\r\n".join(out).decode()
L=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Trail UTHG90//FR","CALSCALE:GREGORIAN","X-WR-CALNAME:Trail UTHG 90","X-WR-TIMEZONE:Europe/Paris"]
stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
for i,(day,t,d) in enumerate(sorted(ev,key=lambda e:e[0])):
    L += ["BEGIN:VEVENT", f"UID:uthg90-{day.isoformat()}-{i}@trail", f"DTSTAMP:{stamp}",
          f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day+dt.timedelta(days=1):%Y%m%d}",
          "SUMMARY:"+esc(t), "DESCRIPTION:"+esc(d+"\n\n"+RULES), "TRANSP:TRANSPARENT", "END:VEVENT"]
L.append("END:VCALENDAR")
open(sys.argv[1],"w",newline="").write("\r\n".join(fold(l) for l in L)+"\r\n")
print(len(ev), min(e[0] for e in ev), max(e[0] for e in ev))
