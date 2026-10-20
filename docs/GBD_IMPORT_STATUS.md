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


## Sverige – tillkommande GBD 2023-exporter (granskade 2026-10-20)

- `IHME-GBD_2023_DATA-80c6414d-1.zip`: Sverige (location_id 93), år **2018–2020**, 7 908 rader.
- `IHME-GBD_2023_DATA-2d4bdc22-1.zip`: Sverige (location_id 93), år **2021–2023**, 7 908 rader.
- Totalt 15 816 unika observationsnycklar; ingen dublett per (measure_id, location_id, sex_id, age_id, cause_id, metric_id, year) inom respektive fil. 380 unika cause_id per fil; år, kön, antal, /100 000, död, DALY samt val/lower/upper.
- Gäller endast **alla åldrar** och **män respektive kvinnor**. Ingen `Both`-kategori i dessa exporter.
- **Ingen riskfaktor**, `rei_id`, PAF eller direkt ICD-mappning. Därför får filerna inte användas för att kvantifiera riskorsakade dödsfall.
- Dessa svenska data kan användas på en separat flik `GBD Sverige – jämförelse` efter dataintegrering och kontroll av jämförbarhet med Socialstyrelsens registerdata.
- Behåll GBD 2023-skattningarna som separata modellerade observationer och markera osäkerhetsintervall; blanda inte ihop GBD-estimat och Socialstyrelsens observerade dödstal.
