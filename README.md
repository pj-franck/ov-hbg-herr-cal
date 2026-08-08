# 🤾 OV Helsingborg Herr – hemmamatcher i din kalender

[![Kalender](https://img.shields.io/badge/Kalender-WebCal-00855f)](webcal://pj-franck.github.io/ov-hbg-herr-cal/ov-hemmamatcher.ics)
[![GitHub Pages](https://img.shields.io/badge/Publicering-GitHub%20Pages-222222)](https://pj-franck.github.io/ov-hbg-herr-cal/)

Prenumerera på OV Helsingborg herrs hemmamatcher direkt i din vanliga kalender.
Kalendern uppdateras automatiskt varje natt från Svenska Handbollförbundets
officiella matchdata.

## Prenumerera

Öppna [kalendersidan](https://pj-franck.github.io/ov-hbg-herr-cal) och välj
**Prenumerera via WebCal**, eller använd länken direkt:

```text
webcal://pjf.se/ov-herr.ics
```

Du kan också [hämta kalenderfilen (.ics)](https://pjf.se/ov-herr.ics).

## Vad ingår?

- OV Helsingborg herrs hemmamatcher i Handbollsligan 2026/27
- Svenska Cupen när förbundet publicerar OV:s herrschema för de senare omgångarna
- Korrekt lokal tid: Europe/Stockholm
- Matchens publicerade arena
- Eventuell matchinfo i kalenderns Notes-fält; annars lämnas fältet tomt

Biljettlänkar och TV-sändningar ingår inte.

## Hur det fungerar

1. GitHub Actions hämtar den offentliga matchdatan varje natt.
2. Endast OV Helsingborgs hemmamatcher i de tillåtna tävlingarna väljs ut.
3. En `.ics`-fil genereras och publiceras på GitHub Pages.

Du kan även köra arbetsflödet manuellt från repots flik **Actions**.

## Utveckling

Projektet kräver Python 3.11 eller senare och har inga externa beroenden.

```text
python -m unittest discover -s tests -v
```

## Datakälla

Matchdata kommer från [Svenska Handbollförbundets Profixio](https://www.profixio.com/app/leagueid28137).

## Licens

Projektet är licensierat under [MIT-licensen](LICENSE).
