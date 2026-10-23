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
# Allures : remplacer par des min/km quand le chrono de référence est connu
ALLURE = {
 "EF": "EF : 5:45-6:15/km sur plat, FC 130-150, tu parles sans effort (oui, c'est lent, c'est voulu)",
 "AM": "allure marathon : 5:00-5:10/km, FC 155-163",
 "SEUIL": "allure seuil : 4:35-4:45/km, FC 165-175",
 "VMA": "allure 5-10 km : 4:00-4:10/km sur 400-1000 m, 4:15-4:25/km sur 1500-2000 m, FC 175+ en fin de répétition",
 "COURT": "30\" à 1' rapide : 3:45-3:55/km, relâché",
}
ECH = "15' échauffement EF + 3 lignes droites, puis "
FIN = ", puis 10' retour au calme EF."
def frac(corps, *zones):
    return ECH + corps + FIN + "\nAllures : " + " | ".join(ALLURE[z] for z in zones) + "\nLieu : plat (berges du Rhône, parc de la Tête d'Or) ou piste. Pluie : tapis."
RENFO_B = "Renfo B (~30 min, complément de début de saison, peut se faire après le vélo) : gainage planche, latéral et superman 3x40s, fentes marchées 3x10/jambe, chaise 3x45s, mollets excentriques sur une marche 3x12, élastique cheville 4 directions 3x15, équilibre 1 pied 3x45s, pompes 3x10."
NUTRI = "Sortie > 2h : teste ta stratégie anti-crampes (500-1000 mg sodium/h, 500-750 ml/h, 60-90 g glucides/h). Note ce que tu prends et si crampes."

ev = []
def add(day, title, desc):
    ev.append((day, title, desc))

def renfo(day, lvl, extra=""):
    add(day, f"💪 Renfo N{lvl}", RENFO[lvl] + (" " + extra if extra else ""))
def velo(day, dur, extra=""):
    add(day, f"🚴 Vélo {dur}", f"Vélo endurance {dur}, tu dois pouvoir discuter. {extra}\n{RAIN_BIKE}")
def repos(day, extra="Repos complet, ou marche / mobilité 20 min."):
    add(day, "😴 Repos", extra)
def run(day, title, desc, long=False):
    d = desc + "\n" + PAIN + "\n" + RAIN_RUN
    if long: d += "\n" + NUTRI
    add(day, "🏃 " + title, d)

# Phase 0
for w in (1,2):
    renfo(D(w,0),1)
    if w==1:
        for d in (1,3,5): run(D(w,d),"Course 25' facile","25' très facile sur plat, sol souple. Reprise : tu dois pouvoir parler en phrases complètes.")
    else:
        run(D(w,1),"Course 30' facile","30' très facile, plat.")
        run(D(w,3),"Course 30' facile","30' très facile, plat.")
        run(D(w,5),"Course 40' facile","40' très facile, plat. Si tout va bien (aucune gêne le lendemain), tu passes en phase 1.")
    velo(D(w,2),"1h-1h30")
    add(D(w,2),"💪 Renfo B",RENFO_B)
    renfo(D(w,4),1)
    velo(D(w,6),"1h30","Ou repos si fatigué.")

# Phase 1: week -> (km, long, D+, light)
p1={3:(22,"1h",0,False),4:(26,"1h10",0,False),5:(30,"1h15",200,False),6:(22,"1h",100,True),
    7:(32,"1h20",300,False),8:(36,"1h30",400,False),9:(40,"1h40",600,False),10:(30,"1h20",300,True)}
for w,(km,ld,dp,light) in p1.items():
    lvl = 1 if w<5 else 2
    lk=round(km*0.35); tk=round(km*0.25); hk=round(km*0.25); sk=km-lk-tk-hk
    if sk<5: lk+=sk; sk=0
    head=f"Base, semaine S{w}"+(" (allégée)" if light else "")+f" : ~{km} km, ~{dp} m D+ au total."
    renfo(D(w,0),lvl)
    P1F={5:"10 x 30\"/30\" (30\" rapide, 30\" trot)",7:"12 x 30\"/30\"",8:"2 séries de 8 x 30\"/30\", 3' trot entre les séries",9:"8 x 1' rapide / 1' trot"}
    if w in P1F:
        run(D(w,1),"Fractionné "+("8 x 1'/1'" if w==9 else "30/30"),head+"\n"+frac(P1F[w],"COURT","EF"))
    else:
        run(D(w,1),f"Course {tk} km EF",head+f"\n{tk} km en endurance fondamentale + 4 lignes droites.\nAllure : "+ALLURE["EF"])
    velo(D(w,2),"1h30-2h")
    add(D(w,2),"💪 Renfo B",RENFO_B)
    if w>=5 and not light:
        run(D(w,3),f"Côtes {hk} km",f"{hk} km au total dont 6 à 8 x 1' en montée à Fourvière, retour en marchant/trottinant.")
    else:
        run(D(w,3),f"Course {hk} km EF",f"{hk} km en endurance fondamentale.")
    renfo(D(w,4),lvl,"Ou repos si la semaine est chargée.")
    run(D(w,5),f"Sortie longue {ld}",f"Sortie longue {ld}, ~{lk} km, très facile. Samoëns : vallée ou raquettes. Lyon : parc, berges, Fourvière."+(" Un peu de D+ (~%d m)."%dp if dp else ""))
    if sk: run(D(w,6),f"Course {sk} km récup",f"{sk} km très facile sur plat, ou vélo 1h30 si tu préfères.")
    else: velo(D(w,6),"1h30","Ou repos.")

# Phase 2 & 3 weeks: (km, D+, long duration, tue quality, phase label, renfo lvl, light?)
Q_COTES_A = "Côtes Fourvière : 15' échauffement EF, 8 x 1'30 en montée (effort soutenu), retour en trottinant/marchant, 10' retour au calme."
Q_SEUIL = "Seuil : 15' échauffement, 3 x 8' à allure seuil (difficile mais tenable 1h), récup 2', 10' retour au calme. Plat ou tapis."
Q_COTES_L = "Côtes longues : 15' échauffement, 4 x 5' en montée (Choulans/Gourguillon ou tapis 10-15%), redescente en courant pour travailler les quadris, 10' calme."
Q_EASY = "Footing facile avec 6 lignes droites, semaine allégée."
Q_SPE = "Côtes longues + marche active : 4 x 6' en montée (alterner course / marche rapide avec bâtons), descentes courues."
weeks = [
 (11,40,1000,"1h45",Q_COTES_A,"Développement A",2,False),
 (12,44,1200,"2h",Q_COTES_A,"Développement A",2,False),
 (13,48,1400,"2h15",Q_COTES_A,"Développement A",2,False),
 (14,34,800,"1h30",Q_EASY,"Développement A (allégée)",2,True),
 (15,48,1400,"2h15",Q_SEUIL,"Développement B",3,False),
 (16,52,1600,"2h30",Q_SEUIL,"Développement B",3,False),
 (17,55,1800,"2h45",Q_SEUIL,"Développement B",3,False),
 (18,40,1000,"2h",Q_EASY,"Développement B (allégée)",3,True),
 (19,55,1800,"2h45",Q_COTES_L,"Développement C",3,False),
 (20,58,2000,"3h",Q_COTES_L,"Développement C",3,False),
 (21,60,2200,"3h15",Q_COTES_L,"Développement C",3,False),
 (22,45,1200,"2h15",Q_EASY,"Développement C (allégée)",3,True),
 (23,55,2200,"3h",Q_SPE,"Spécifique D",3,False),
 (24,60,2600,"3h30",Q_SPE,"Spécifique D",3,False),
 (25,65,3000,"4h",Q_SPE,"Spécifique D",3,False),
 (26,45,1500,"2h30",Q_EASY,"Spécifique D (allégée)",3,True),
 (27,62,2800,"4h",Q_SEUIL,"Spécifique E",3,False),
 (28,None,None,None,Q_EASY,"Course de prépa",3,True),
 (29,50,2000,"3h",Q_EASY,"Spécifique E (reprise après course)",3,True),
 (30,70,4000,"5-6h",Q_SPE,"Spécifique E (semaine choc)",3,False),
 (31,50,2500,"3h",Q_SEUIL,"Affûtage -30%",3,False),
 (32,38,1500,"2h30 max",Q_EASY,"Affûtage -45%",3,True),
 (33,25,800,None,Q_EASY,"Affûtage -60% / semaine de course",3,True),
]
for (w,km,dp,ld,q,lab,lvl,light) in weeks:
    head = f"{lab}, semaine S{w}" + (f" : ~{km} km, ~{dp} m D+ au total." if km else ".")
    if w==28:
        renfo(D(w,0),3,"Version légère : 2 séries au lieu de 3.")
        run(D(w,1),"Footing 40' + 4 lignes droites", head + " Facile.")
        velo(D(w,2),"1h","Très facile.")
        run(D(w,3),"Footing 30' facile", head)
        repos(D(w,4),"Repos, prépare ton matériel et ta nutrition de course.")
        run(D(w,5),"COURSE DE PRÉPA (40-60 km) – à choisir", "Course de préparation, à placer ce week-end (samedi ou dimanche). Répétition générale : allure (1re moitié facile, marche dans les montées raides), nutrition, sel, matériel.", long=True)
        repos(D(w,6),"Repos ou marche. Si la course est dimanche, inverse avec samedi.")
        continue
    if w==33:
        renfo(D(w,0),3,"Version très légère, pas de charges lourdes.")
        run(D(w,1),"Footing 40' + 3 x 3' allure course", head + " Allure course UTHG : très facile, objectif réaliste 13:30-14:30/km de moyenne tout compris (à affiner sur la course de prépa).")
        velo(D(w,2),"45'","Très facile.")
        run(D(w,3),"Footing 30' facile", "Jambes légères.")
        repos(D(w,4),"Repos. À ajuster quand la date exacte de l'UTHG 90 est connue.")
        add(D(w,5),"🏔️ UTHG 90 km (date à confirmer)","Semaine de course. Déplace cet événement à la vraie date de l'UTHG 2027. Départ facile, tu marches toutes les montées raides, sel + glucides dès la 1re heure.")
        repos(D(w,6),"Récupération.")
        continue
    renfo(D(w,0),lvl)
    TUE={11:"10 x 400 m, récup 1' trot",12:"6 x 800 m, récup 1'30",13:"5 x 1000 m, récup 2'",
         15:"6 x 1000 m, récup 1'30",16:"4 x 1500 m, récup 2'",17:"3 x 2000 m, récup 2'30",
         19:"6 x 1000 m, récup 1'30",20:"5 x 1200 m, récup 1'30",21:"4 x 2000 m, récup 2'",31:"6 x 1000 m, récup 1'30"}
    THU={23:("Seuil 2 x 15'",frac("2 x 15' allure seuil, récup 3'","SEUIL","EF")),
         24:("Seuil 3 x 12'",frac("3 x 12' allure seuil, récup 2'","SEUIL","EF")),
         25:("Tempo 40' vallonné",frac("40' allure marathon sur parcours vallonné","AM","EF")),
         27:("Seuil 3 x 10'",frac("3 x 10' allure seuil, récup 2'","SEUIL","EF")),
         30:("Tempo 30'",frac("30' allure marathon","AM","EF")),
         31:("Seuil 2 x 10'",frac("2 x 10' allure seuil, récup 2'","SEUIL","EF"))}
    if light:
        run(D(w,1),"Fractionné court 8 x 30/30", head+"\n"+frac("8 x 30\"/30\" pour garder de la vitesse sans fatigue","COURT","EF"))
    elif w in TUE:
        run(D(w,1),"Fractionné " + TUE[w].split(",")[0], head+"\n"+frac(TUE[w]+(", à allure 10 km" if w>=17 else ", à allure 5-10 km"),"VMA","EF"))
    else:
        run(D(w,1),"Côtes spécifiques", head + "\n" + q)
    if w < 23:
        velo(D(w,2),"1h30-2h","Si fatigue, tu peux le remplacer par du repos.")
        if not light: add(D(w,2),"💪 Renfo B",RENFO_B)
    else:
        velo(D(w,2),"1h30","Ou 45' de course facile si le vélo n'est pas dispo.")
    tk = round(km*0.22)
    if light:
        run(D(w,3), f"Course {tk} km EF vallonné", f"{tk} km en endurance, parcours vallonné.\nAllure : "+ALLURE["EF"])
    elif w in THU:
        run(D(w,3), THU[w][0], THU[w][1])
    else:
        run(D(w,3), "Qualité : " + q.split(":")[0], q + "\nSi tu te sens fatigué après le fractionné de mardi, fais plutôt 45' EF vallonné.\nAllures : effort soutenu en montée (7-8/10), retour EF.")
    renfo(D(w,4),lvl,"Ou repos. Jamais la veille d'une grosse sortie longue : si besoin déplace-le au jeudi.")
    lk = round(km*0.40)
    run(D(w,5), f"Sortie longue {ld}" + (" (Samoëns ou Fourvière)" if w<23 else " montagne"),
        f"Sortie longue {ld}, ~{lk} km, en EF (allure libre dans les montées, marche si ça grimpe fort). Samoëns : en montagne avec D+ (raquettes ou ski de rando OK si neige). Lyon : boucles Fourvière (Choulans, Gourguillon, Chazeaux) ou tapis incliné." , long=True)
    sk = km - tk - lk - round(km*0.2)
    sk = max(sk, round(km*0.18))
    if w>=23 and not light:
        run(D(w,6), f"Enchaînement {sk} km facile", f"Lendemain de sortie longue : {sk} km facile sur jambes fatiguées. Idéal en montagne à Samoëns.")
    else:
        run(D(w,6), f"Course {sk} km récup", f"{sk} km très facile, récupération. Ou vélo 1h30 si tu préfères.")

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
for e in sorted(ev)[:8]+sorted(ev)[63:70]+sorted(ev)[-7:]: print(e[0], e[1])
