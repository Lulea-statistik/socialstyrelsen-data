# Källgranskning – SCB dödsorsaker (2026-10-20)

## Identifierade officiella dokument

1. SCB Jämställdhetsstatistik, produkt **LE0201**: https://www.scb.se/le0201 – ingång för kvalitetsdeklarationer (2025 m.fl.) samt *Statistikens framställning* (2026 m.fl.). Dessa är primära dokument för hur tabell 5.25/5.26 publiceras.
2. SCB tabell 5.26 (Tema526N): https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201H%C3%A4lsa/Tema526N/ – personer 35–84 år, dödsorsak, utbildningsnivå, kön, 2020–2025. Senast uppdaterad 2026-10-15. Fotnot: utbildningsnivå baseras på 2019 års uppgifter; äldre årgångar kan revideras.
3. SCB kvalitetsdeklaration Jämställdhetsstatistik 2023, LE0201: https://www.scb.se/contentassets/2a4d8b96c4cf4ee88d05034b77717d1e/le0201_kd_2023.pdf – produktövergripande dokument, **inte** komplett kodlista för tabellens dödsorsaksgrupper.
4. Socialstyrelsens dödsorsaksstatistik, kvalitetsdeklaration 2020, HS0301: https://www.scb.se/contentassets/692abc00759c49b99539fc4bc92a2feb/hs0301_kd_2020.pdf – ICD-10, mått, utbildning, åldersstandardisering, diagnosers tillförlitlighet. Relevant bakgrund, **inte** bevis för identisk gruppdefinition i SCB:s tabell.
5. SCB *På tal om kvinnor och män 2026*: https://www.scb.se/hitta-statistik/statistik-efter-amne/befolkning-och-levnadsforhallanden/jamstalldhet/jamstalldhetsstatistik/produktrelaterat/rapporter/kvinnor-och-man-2026 – publicerar dödstal för kvinnor/män efter utbildning, beskriver dem som åldersstandardiserade. Dessa kan bli referensvärden för kontroller.

## Kontrollpunkter som fortfarande kräver belägg

- **Tecknet `..`:** 160 originalceller i Tema525 har `..`, bekräftat i vårt API-svar. Vi har **inte** belagt från tabellspecifik officiell teckenförklaring att varje `..` betyder sekretess på grund av liten population. Kodas som `non_numeric_original_marker` tills dess.
- **Åldersstandardisering:** API-tabell 5.26 anger antal döda per 100 000 medelfolkmängd; publikationen 2026 använder formuleringen åldersstandardiserade dödstal. Granska specifikt om tabell 5.26 faktiskt är åldersstandardiserad och i så fall mot vilken standardpopulation, före jämförelse.
- **Exakta ICD-urval:** Ingen kvalitetsdeklaration som hittats ger entydig, tabellspecifik kodlista för alla 11 grupper. Kodmappningen förblir blockerad.
- **Seriebrott och klassifikation:** utbildningsnivå enligt SUN, uppgifter baserade på 2019. Skilj 35–79 (äldre tabell) från 35–84 (aktuell tabell).
- **Källhierarki:** LE0201 dokumenterar SCB:s sammanställning; HS0301/Socialstyrelsen dokumenterar underliggande dödsorsaksregister. Båda kan behövas, men ersätter inte en tabellspecifik avgränsning.

## Fortsatt validering

1. Hämta och granska **LE0201 Statistikens framställning 2026** samt aktuell kvalitetsdeklaration 2025, särskilt bilagor om tabell 5.25/5.26, sekretess och metod.
2. Fastställ teckenförklaring för `..` skriftligt. Använd aldrig nollsubstitution.
3. Verifiera om data i Tema526N är åldersstandardiserade och om referensvärdena i *På tal om kvinnor och män 2026* matchar.
4. Begär SCB:s/Socialstyrelsens exakta ICD-urvalslista för grupper som saknar publicerad specifikation.
5. Låt `approved_for_aggregation=false` gälla tills varje matchning kan styrkas separat.

Denna anteckning är en **källinventering och riskbedömning**, inte en färdig ICD-validering.
