# OV Helsingborg Herr – Hemmamatcher i kalendern

En prenumererbar kalender med OV Helsingborgs herrlags hemmamatcher.

Projektet hämtar matchdata från Svenska Handbollförbundets offentliga
Profixio-sidor och ska på sikt publicera en `.ics`-fil som går att prenumerera
på via WebCal. Kalenderlogik, filtrering och automatisering tillkommer i
senare steg.

## Status

Steg 2 är klart: hämtaren kan läsa alla matcher från en angiven officiell
Profixio-länk. Den filtrerar ännu inte på herrlag, hemmamatcher eller tävling
och genererar ingen kalenderfil.

## Utveckling

Projektet kräver Python 3.11 eller senare och har inga externa beroenden.

```text
python -m unittest discover -s tests
```

## Planerad användning

När projektet är klart kommer kalendern att kunna prenumereras på via en WebCal-länk, exempelvis:

```text
webcal://pj-franck.github.io/ov-hbg-herr-cal/ov-hemmamatcher.ics
```

## Struktur

```text
src/                Projektets Python-kod
.github/workflows/  GitHub Actions-arbetsflöden (kommer i senare steg)
tests/              Tester och HTML-fixtures för datakällan
```

## Licens

Projektet är licensierat under [MIT-licensen](LICENSE).
