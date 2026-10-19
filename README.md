# Socialstyrelsens statistik

Webbplats i `main/docs` med en första utforskare för dödsorsaksstatistik.

Publiceringsadress efter aktiverad GitHub Pages: https://lulea-statistik.github.io/socialstyrelsen-data/

## Starta

1. Kör **Actions → Bygg Socialstyrelsens data → Run workflow**. Arbetsflödet hämtar Socialstyrelsens CSV-arkiv och producerar `docs/data/dodsorsaker.json`.
2. Aktivera **Settings → Pages → Deploy from a branch → main /docs**.

## Data

Den första versionen visar endast ett urval av diagnoskoder och total ålder, för riket och län. Måtten är antal döda och antal per 100 000 invånare. Sistnämnda är inte åldersstandardiserat. Överlappande diagnosgrupper får inte summeras. Sekretessmarkerade/saknade observationer behandlas inte som noll.

Källa: https://www.socialstyrelsen.se/statistik-och-data/statistik/for-utvecklare/

Planerat: ekonomiskt bistånd samt graviditeter, förlossningar och nyfödda.
