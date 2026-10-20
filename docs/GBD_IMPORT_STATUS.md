# GBD 2023 – granskning av användarens export

**Arkiv:** IHME-GBD_2023_DATA-74d5078f-1.zip

## Validerat
- 81 716 datarader; 380 olika `cause_name`-etiketter.
- `location_name` är uteslutande **Global** (location_id=1), **inte Sverige**.
- År 1990–2020 (31 årsserier).
- `measure_name`: Död och DALY.
- `metric_name`: Antal och /100,000.
- `sex_name`: Män, Kvinnor; `age_name`: Alla åldrar.
- Numeriska värden `val`, `lower`, `upper` är publicerade GBD-skattningar och osäkerhetsintervall.
- `cause_id` finns, vilket möjliggör robust identifiering av GBD-orsaker.
- **Ingen `rei_id` eller `rei_name`**, ingen PAF. Filen är sjukdomsbörda efter dödsorsak, **inte** riskattribuerbar sjukdomsbörda.
- Denna export är inte i sig en officiell ICD-10-kodlista. Knyt inte direkt till Socialstyrelsens diagnoser utan särskild validerad mappning.

## Statistisk avgränsning
- Får **inte** jämföras som Sverige- eller länsstatistik.
- Får **inte** användas för att tillskriva en viss andel av dödsfallen till miljö/genetik/levnadsvanor.
- För globala trender kan data användas som en separat serie märkt `GBD 2023 • Global`, med datautgåva, mått, enhet, kön och osäkerhet.

## Begärd komplettering för analysfliken
I IHME GBD Results: välj **Sweden**, **Deaths**, **Percent / PAF** (när måttet erbjuds i Risk factors), **Risk factors**, önskade orsaker, år, kön och ålder. Exportera också attribuerbara dödsfall (Number), samt osäkerhetsintervallen. Behåll ursprungliga GBD cause_id och rei_id och dokumentera exportinställningar och licens.

## Källhänvisning (medföljande citation.txt)
Global Burden of Disease Collaborative Network. Global Burden of Disease Study 2023 (GBD 2023) Results. Seattle, United States: Institute for Health Metrics and Evaluation (IHME), 2024. https://vizhub.healthdata.org/gbd-results/
