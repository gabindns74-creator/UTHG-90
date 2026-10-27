# Plan trail UTHG 90

Calendrier d'entraînement vers l'UTHG 90 km (juin 2027).

- `plan-uthg90.ics` : le calendrier, à suivre en abonnement depuis Apple Calendar.
- `generate_calendar.py` : génère le fichier (`python3 generate_calendar.py plan-uthg90.ics`).
- `ajustements.json` : prévisions Meteoblue Lyon et échanges de séances selon la météo, appliqués à la génération.

Adresse d'abonnement :
`webcal://raw.githubusercontent.com/gabindns74-creator/UTHG-90/main/plan-uthg90.ics`

## Séances réalisées

`sync_seances.py` récupère les séances (montre Garmin → intervals.icu, gratuit) deux fois par jour via GitHub Actions et écrit :

- `seances/activites.csv` : une ligne par séance (sport, km, durée, allure, D+, FC, charge, ressenti).
- `seances/bien-etre.csv` : FC de repos, HRV, sommeil, forme/fatigue.
- `seances/resume.md` : volume par semaine, pour comparer au plan.

Aucune trace GPS ni lieu n'est enregistré (repo public). La clé API est le secret `INTERVALS_API_KEY` du repo.
