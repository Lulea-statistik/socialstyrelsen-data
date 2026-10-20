# SCB–Socialstyrelsen: definitionsvalidering av dödsorsaker

Status: **pågående, ej godkänd för ICD-aggregering**. Uppdaterad 2026-10-20.

## Officiella källor och verifierade förutsättningar

- SCB, Tabell 5.26 (Tema526N): https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201H%C3%A4lsa/Tema526N/
  - Dödsorsaker för personer **35–84 år** efter utbildningsnivå, kön och år.
  - Måttet är **antal döda per 100 000 av medelfolkmängden**, inte antal dödsfall.
  - Utbildningsnivå enligt SUN; tabellens fotnot uppger att utbildningsnivån baseras på **2019 års uppgifter**.
  - Historiska värden kan revideras när nya årgångar publiceras.
- SCB äldre Tabell 5.26 (Tema526): https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201%C3%96/Tema526/
  - Gäller **35–79 år** 2017–2019. Får inte direkt fogas till serien för 35–84 år.
- Socialstyrelsens dödsorsaksdatabas: https://sdb.socialstyrelsen.se/if_dor/val.aspx
  - Underliggande dödsorsak enligt internationell ICD-10; folkbokförda i Sverige.
- Kandidatgrupper och metadataavstämning: [scb-icd-crosswalk-audit.json](data/scb-icd-crosswalk-audit.json).

## Gruppvis granskningskö

| SCB-grupp | Socialstyrelsen-kandidat | Definitionstest som återstår | Beslut |
|---|---|---|---|
| totalt | 99 | Alla åldrar kontra tabellens åldersavgränsning; jämför källa och mått | Ej godkänd |
| totalt 35–84 år | 99 | Filtrera exakt 35–84 år, kön och år; jämför nämnare | Ej godkänd |
| andningsorganens sjukdomar | J00–J99 | Stäm av om SCB använder hela ICD-kapitlet | Ej godkänd |
| hjärt-kärlsjukdomar | I00–I99 | SCB:s hjärt-kärldefinition kan vara snävare än cirkulationsorganens sjukdomar | Ej godkänd |
| tumörer | C00–D48 | Verifiera inkluderade tumörtyper och klassifikationsversion | Ej godkänd |
| alkoholrelaterad dödlighet | Alk | Kontrollera officiell urvalslista/underliggande dödsorsak och möjlig annan definition | Ej godkänd |
| därav alkoholrelaterad dödlighet | Alk | Verifiera överordnad grupp och dubbelräkningsrisk | Ej godkänd |
| därav Covid-19 | U07 | Kontrollera exakt underkod, år och inkluderingsregler | Ej godkänd |
| självmord och skadehändelse med oklar avsikt | X60–X84 + Y10–Y34 | Kontrollera fullständig officiell koduppsättning, gränser och eventuella tillägg | Ej godkänd |
| skador och förgiftningar exkl. oklar avsikt | V01–Y98 | **Får inte användas rakt av:** omfattar även Y10–Y34, som uttryckligen ska exkluderas; kontrollera även självmord och andra delkategorier | Ej godkänd |
| övrigt | residual | Kräver officiell definition och disjunkta, uttömmande grupper innan rest beräknas | Ej godkänd |

## Hårda kvalitetsregler

1. **Ingen automatisk aggregering** för en grupp med `approved_for_aggregation=false`.
2. Att en ICD-kod existerar i Socialstyrelsens metadata är **inte** bevis för identisk definition.
3. Jämför **antal med antal** och **dödstal med dödstal**. Summera aldrig publicerade dödstal för olika undergrupper utan korrekta befolkningsvikter.
4. Kontrollera ålder, kön, år, definition av utbildning, dödsorsaksklassificering och population.
5. SCB:s tabeller kan **återpubliceras som egna SCB-serier** utan omräkning till Socialstyrelsens ICD-grupper, under tydlig källmärkning. Detta innebär inte att deras utbildningsuppgifter kan tilldelas Socialstyrelsens kommunvärden.
6. SCB:s äldre 35–79-årsserie och senare 35–84-årsserie ska behandlas som skilda populationer utan omräkningsunderlag.
7. SCB-grupper markerade 'därav' kan överlappa andra grupper; en totalsumma av grupper är inte giltig utan bevisad disjunkthet.
8. Varje framtida godkännande kräver versionslåst kodlista/SCB-definition, käll-URL, kontroll av enhet och test mot publicerade referensvärden.

## Nästa granskningssteg

1. Hämta metadata och samtliga fotnoter via **SCB API**, dokumentera variabelkoder och versionsdatum.
2. Sök SCB:s officiella ICD-urvalsdefinition per grupp. Om definitionen saknas: kvarstå i ej godkänt läge.
3. Bygg testspecifikation med officiella referensvärden efter kön, år och ålder; inga numeriska jämförelser genomförda i denna anteckning.
4. Godkänn endast enskilda mappningar med explicit evidens. Låt övriga förbli separata SCB-serier.

Denna fil dokumenterar genomförd källkontroll och återstående uppgifter; den intygar **inte** att fullständig definitionsvalidering genomförts.
