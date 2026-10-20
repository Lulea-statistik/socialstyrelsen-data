# Dödsorsaksgrupper, ålder och utbildning – SCB

Källor:
- https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201H%C3%A4lsa/Tema525/
- https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__LE__LE0201__LE0201H%C3%A4lsa/Tema526N/

## Mätning
SCB 5.25: 2017–2025, dödsorsak, ålder, kön och dödstal.
SCB 5.26: 2020–2025, 35–84 år, dödsorsak, kön, utbildning enligt SUN (förgymnasial, gymnasial, eftergymnasial), dödstal per 100 000 av medelbefolkningen. Utbildning är baserad på 2019 års uppgifter.

## Gruppering
SCB:s grupper är en separat officiell indelning. En grupp med `därav` är en delmängd och **får inte adderas** till grundgrupperna eller totalt.
*En gemensam etikett är inte en validerad ICD-10-koppling.* Om Socialstyrelsens detaljposter ska aggregeras enligt SCB:s indelning krävs källverifierade ICD-listor, särskilt för alkoholrelaterade dödsfall, Covid-19, oklar avsikt, skador och övrigt. Ingen sådan mappning får antas utifrån rubriken ensam.

## Tolkning av utbildning
Skillnader i dödstal efter utbildning är **associationsmått på gruppnivå**, inte kausala effekter av utbildning. Kontrollera i originalstatistiken om dödstalen är åldersstandardiserade, annars kan utbildningsgruppernas olika åldersstruktur bidra till skillnaderna. Utbildningsgrupperna kan ha varierande täckning och ändringar; täljare och nämnare måste vara konsistenta.

## Datastatus
Skriptet `scripts/build_scb_mortality_education.py` hämtar de officiella serierna via SCB PxWeb-API och skriver `docs/data/scb-mortality-education.json`. Efter första lyckade körningen ska validering av antal observationer, tabellmått och kodlistor göras. Statistikfliken visar SCB:s egen indelning; Socialstyrelsens detaljserier är fortsatt fristående tills ICD-mappning är verifierad.

## Verifiering efter arbetsflöde #2
- SCB 5.25: 848 numeriska observationer; 8 officiella dödsorsaksrubriker; 7 åldersgrupper; båda könen; 2017–2025.
- SCB 5.26: 324 numeriska observationer; 9 rubriker inklusive två `därav`-grupper; 3 utbildningsnivåer; båda könen; 2020–2025.
- SCB:s utdrag 5.25 har ett tabellinnehåll med kod `0000034O`, vars kortetikett är `Antal` men tabellrubriken säger **antal döda per 100 000 av medelbefolkningen**. Källa och definition kontrolleras före jämförelse med detaljregister.
- Den separata utbildningsfliken visar senast publicerat års absolut skillnad och kvot mellan förgymnasial och eftergymnasial grupp när båda värden finns.
