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
