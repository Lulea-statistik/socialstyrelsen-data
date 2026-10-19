# Riskfaktorer och dödsorsaker – metod och datastatus

## Källor
- Officiell GBD-resursöversikt: https://ghdx.healthdata.org/gbd-2021/data-input-sources
- GBD 2021 riskbörda: https://ghdx.healthdata.org/record/ihme-data/gbd-2021-burden-by-risk-1990-2021
- GBD Results: https://vizhub.healthdata.org/gbd-results/

## Evidensnivåer
1. Dokumenterade kopplingar: kodmappning och risk–orsakspar verifierade mot IHME:s officiella tabeller.
2. Kvantitativa skattningar: originalvärde, osäkerhetsintervall, utgåva, land, år, kön, ålder, risk, utfall och källa.
3. Scenarier: uttryckligen hypotetiska och aldrig likställda med GBD-resultat.

## Kvalitetsgränser
- Inget numeriskt PAF utan verifierad orsak–risk-koppling, källa och användningsrätt.
- Heritabilitet får inte tolkas som andelen dödsfall som orsakats av gener.
- Attribution över riskfaktorer är normalt icke-additiv.
- Undvik att multiplicera en nationell PAF med länsdödsfall och presentera resultatet som en observerad länsskattning.
- GBD:s dödsorsaker använder omfördelning av ospecifika ICD-koder och harmonisering, och är inte alltid direkt jämförbara med Socialstyrelsens ursprungliga dödsorsaksvärden.
- Granskningsstatus i `docs/data/gbd-crosswalk-review.json` är endast förslag, inte verifierade mappningar.
- Kvalitetssäkrad import via `python scripts/validate_gbd.py data/gbd-reviewed.csv` kräver uttrycklig granskning även av licensen.

## Nästa blockerare
Hämta officiell GBD 2021 cause-to-ICD-lista, risk-to-cause-relationer samt relevanta svenska PAF-serier från IHME. Detta kan kräva registrerat konto, och källans villkor måste godkännas innan publicering.
