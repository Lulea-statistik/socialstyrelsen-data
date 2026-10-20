# BMI och barnafödande – studieupplägg

## Vad mäts?
- SCB ULF (Tema515N): skattad BMI-fördelning i befolkningen, efter kön/ålder och intervall, med osäkerhet.
- Socialstyrelsen medicinska födelseregistret: BMI vid inskrivning bland personer med graviditet som resulterade i förlossning och andra variabler om förlossningar.
- SCB befolkningsstatistik: antal kvinnor per åldersgrupp och år som nödvändig nämnare för åldersspecifika födelsetal (ska hämtas separat).

## Prioriterade analyser
1. Separata trender: kvinnor i SCB ULF och gravida vid inskrivning. Presentera nivåskillnader utan att kalla dem skillnad i fertilitet.
2. Välj först jämförbara åldersgrupper och harmoniserade BMI-kategorier. Visa då eventuell differens i procentenheter och urvalsosäkerhet.
3. Med födslar och befolkningsnämnare: undersök födelsetal per 1 000 kvinnor, med åldersstandardisering och kontroll för tidsutveckling.
4. Explorativ korrelation mellan BMI-andel och födelsetal: både rå korrelation, trendrensad/årsvis förändring och tidsförskjutningar. Rapportera n, r, osäkerhet samt utelämnade år. Ingen kausal slutsats.
5. Negativ kontroll: jämför olika åldersband och se om slutsatsen ändras.
6. För sannolikheten att bli gravid krävs longitudinell data om försök att bli gravid eller trovärdiga fertilitetsstudier; förlossningsregistret kan inte svara.

## Kvalitetskrav
- SCB:s fleråriga perioder ska inte automatiskt tilldelas samma värde varje år.
- Blanda inte urvalsskattningar och registerantal utan måttenhetskontroll.
- Börja med rikstrender: ULF-tabellen saknar i denna export länsvariabel.
- Undvik BMI-värden mätta efter graviditetens början som direkta mått på BMI före befruktning.
- Kontrollera eventuella definitionsbrott och om BMI-kategorierna summerar till 100 inom samma nämnare.
- Sekretessmarkeringar, .. och saknade värden är inte noll.

## Källor
- https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201H%C3%A4lsa/Tema515N/
- https://sdb.socialstyrelsen.se/
- https://www.statistikdatabasen.scb.se/

Datakällornas faktiska variabellistor och kategorier sparas först i `docs/data/bmi-source-series.json` via GitHub Actions. Ingen korrelationskoefficient publiceras före harmonisering och kvalitetstest.

## Inventering efter BMI-källserier #2 (2026-10-20)
Automatiserad kontroll: `docs/data/bmi-audit.json`.
- SCB ULF: 2 080 rader totalt (inklusive osäkerhetstal). 4 BMI-klasser; kvinnor och män; 5 åldersgrupper (16–84, 16–29, 30–49, 50–64, 65–84 år). 26 tidsintervall, från 1980–1981 till 2025–2025. **560 poster med `..`**, blandat uppskattade värden och osäkerhetsmått; dessa får inte tolkas som noll.
- Socialstyrelsen MFR: 117 450 BMI-rader i källdatafilen; 33 årsserier från 1992; 22 regionkoder; fem mätvariabler: undervikt (V02), normalvikt (V03), övervikt (V04), obesitas (V05), BMI-medelvärde (V06).
- MFR har sex ålderskoder, tre paritetskoder och tre måttkoder. Dessa måste först avkodas mot arkivets metadata för att välja korrekt nämnare och enhet. Riksnivå har regionkod `00000`. MFR-populationen är förlossningar, inte alla som försöker bli gravida.
- **Betydande åldersmismatch:** SCB delar 16–49 i 16–29 och 30–49, medan MFR använder egna kategorier. Vi får inte göra en skenbart exakt åldersmatchning.
- Flerårsperioder i SCB är inte årsvisa mätningar. Seriell trend och osäkerhet måste beaktas före Pearsons r/regression.

## Folkhälsomyndigheten som sammanhang och jämförelsekälla
- https://www.folkhalsomyndigheten.se/vara-amnesomraden/overvikt-och-obesitas/overvikt-och-obesitas-i-befolkningen/
- Myndighetens sammanställning använder ULF, HLV och MFR och visar att BMI ≥25 respektive BMI ≥30 generellt ökat bland vuxna och gravida, samtidigt som olika mätmetoder och ålderssammansättningar behöver beaktas.
- Sidan hänvisar till särskild statistik om BMI bland gravida och till FolkhälsoStudio. Detta används som kontext och triangulering – inte som självständig observation i korrelationsanalysen för att undvika dubblering av ULF/MFR.
- Referenskategorierna överensstämmer definitionsmässigt på BMI-gränser: <18,5; 18,5–24,9; 25–29,9; ≥30. **Överensstämmande BMI-gränser innebär dock inte jämförbara undersökningspopulationer.**

## Prioritet kommande körning
1. Avkoda MFR:s meta - mått/åldrar/paritet/region för korrekt användning av andelar och nämnare.
2. Skapa en avgränsad svensk långtidstabell med kvinnor ULF 16–29 och 30–49 samt MFR åldersgrupper, där råår/årsintervall framgår uttryckligen.
3. Importera SCB:s åldersspecifika födelsetal och befolkningsnämnare innan regression mellan befolknings-BMI och barnafödande.
