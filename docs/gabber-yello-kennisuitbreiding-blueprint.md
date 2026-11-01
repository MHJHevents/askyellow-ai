# Gabber Yello Kennisuitbreiding Blueprint

Versie 1.20 — 1 november 2026

## Doel en uitgangspunt
Breid de bestaande goedgekeurde hardcorekennis uit. Maak geen nieuwe basisronde die het eerdere werk herhaalt. Lever volledige themadocumenten aan, met relevante aanvullingen bij het bestaande onderwerp of in een duidelijk aanvullingshoofdstuk. Dennis, Fer en hun medecontroleur lezen de documenten; hun feedback wordt per ronde verwerkt.

## Reviewprotocol
- Bestaande kennis blijft zwart.
- Nieuwe inhoud en nieuwe correcties staan in rode letters, ook als een correctie van de assistent zelf komt.
- Goedgekeurde aanvullingen krijgen zwarte letters met gele markering. Geel betekent inhoudelijk goedgekeurd, niet gedeployed.
- Gebruikerscommentaar en afkeur staan blauw. Behoud die feedback traceerbaar en op de relevante plek.
- Geen bezwaar bij een volledig nagekeken aanvulling mag als akkoord worden verwerkt; ontbrekend commentaar zonder reviewbevestiging niet automatisch.
- Verwerk een afgekeurde claim niet ongemerkt in het kennisbankmateriaal. Leg de reactie blauw vast en leg eventueel een vervangende formulering rood opnieuw voor.
- Bewaar de ontvangen reviewversie en de versiegeschiedenis. In de uiteindelijke kennisbank komt alleen de goedgekeurde inhoud, niet de reviewvragen en commentaren.

## Zeven thema’s
1. Hardcore basis
2. Artiesten dj’s en liveacts
3. Feesten clubs en de geschiedenis van de scene
4. Kleding dansstijl en typische gebruiken
5. Platen labels en bekende tracks
6. Hardcoretermen en gewone Nederlandse betekenissen
7. MHJH smaak eigen mening en persona

## Kennis en bronnen
- Maak onderscheid tussen bevestigd feit, scenegebruik, betwiste geschiedenis, persoonlijke herinnering en mening.
- Verzamel gericht via artiesten, labels, organisatoren, archieven en interviews. Gebruik crawlen alleen als invoer voor controle, nooit als automatische waarheid in de kennisbank.
- Vermeld bron en controledatum bij nieuwe feitelijke kennis. Buitenlandse namen die reviewers niet kennen worden door de assistent geverifieerd.
- Jullie MHJH-ervaringen mogen als toegeschreven interne kennis worden opgenomen; smaak wordt geen objectief feit.
- Privé- en inside-informatie is niet automatisch publiceerbaar. Met name privébezit en archiefopslag van Mirko blijven buiten de publieke kennis zonder toestemming.
- Historische kennis blijft gescheiden van actuele boekingen, releases, line-ups en data. Recente of nieuwste claims vereisen een actuele bron en peildatum; bij ontbreken eerlijk onzeker zijn.
- Nieuwe feiten uit een bezoekerschatsessie worden niet automatisch algemene kennis voor andere gebruikers. Persoonlijk geheugen en goedgekeurde gedeelde kennis blijven gescheiden.
- Haal per vraag alleen relevante kennis op. Een grotere kennisbank betekent niet dat elk gesprek het hele archief meestuurt. Blijf tokengebruik per functie volgen.

## Werkvolgorde
Volledige aanvulling schrijven → broncontrole → Word met rood → menselijke review in blauw → verwerking met geel en eventuele nieuwe rode voorstellen → inhoudelijk akkoord → gecontroleerde selectie voor kennisbank → staging → gerichte tests → expliciete gouden knop voor live.
Tijdens menselijke review kan het volgende document worden voorbereid binnen een actieve werksessie. Er draait niet vanzelf een achtergrondtaak na het afsluiten van een gesprek.

## Bevestigde stand op 29 oktober 2026
- Ronde 1: ontvangen Word met vier blauwe antwoorden. Geen bezwaren bij de aanvulling. Kernpunt over geleidelijke en doorlopende ontwikkeling verwerkt als scenevisie waar het de toekomst betreft. Goedgekeurde aanvullingen geel.
- Ronde 2: ontvangen Word met vier blauwe antwoorden. Dr. Peacock al aanwezig in de basis; verdieping toegevoegd. Ruffians dj-rol en bij MHJH gedraaide set toegevoegd op aanwijzing van Dennis en Fer, met bronattributie.
- Ronde 2: fout in eerdere assistenttekst over herkomst van The Satan gevonden bij eigen broncontrole. Frankrijk vervangen door Rusland. Dennis heeft daarna beide rondes expliciet volledig goedgekeurd, inclusief de twee nog rode passages.
- De aangeleverde blauwe opmerkingen zijn behouden; geen woordelijke feedback gewist.
- De Word-reviewbestanden blijven als reviewhistorie bestaan; hun laatste rode passages zijn door de latere expliciete chatgoedkeuring inhoudelijk afgerond.
- Alleen de goedgekeurde aanvullingen zijn in de bestaande Markdown-kennisbestanden verwerkt. Geen nieuwe blauwe reviewantwoorden of redactionele commentaren naar de runtime gekopieerd.
- Verwijzingen naar de programmering van Den Haag Hakkûh II in ronde 2 zijn gedateerd als historische programmering van 17 oktober 2026; daarmee is geen daadwerkelijk gespeelde set bewezen.
- Ronde 1 en 2 zijn samen met negen offline retrievalcontroles en deze blueprint naar MHJHevents/askyellow-staging op branch main doorgezet. De bestaande kennisselectie, limiet van drie passages en contextbudget zijn ongewijzigd.
- De negen lokale retrievalcontroles slagen. Dit controleert kennisselectie, niet het daadwerkelijke modelantwoord of de Render-deploy.
- Dennis heeft de stagingchat getest met de vraag over The Satan. Het gedeelde antwoord benoemt Rusland, hardcore, drum-and-bass en breakcore correct. Op basis daarvan gaf Dennis op 29 oktober 2026 expliciet de gouden knop voor beide rondes.
- Productierepository askyellow-ai/main is bijgewerkt met uitsluitend beide goedgekeurde kennisbestanden en de bijbehorende offline test. Commit: bea850a5fedb031626fe8942481ea380ce5593b4. Voorgaande livecommit voor een eventuele gerichte rollback: 123fedd7c2265bb815889117d7c2075c620e4dcb.
- De negen retrievalcontroles slagen ook met de bestaande live-kennisloader en de overige live-kennisbestanden. Nieuwe kennisbestanden zijn inhoudelijk identiek aan de geaccepteerde stagingversie. Geen databases, secrets of overige livecode gewijzigd.
- GitHub meldt geen deploystatussen voor deze commit. De productiefunctionaliteit is wel onafhankelijk gecontroleerd: /health geeft HTTP 200, env live en db_ok true. Een nieuwe geïsoleerde gastchat op de live-API geeft The Satan als artiest uit Rusland met hardcore, drum-and-bass en breakcore; knowledge_used=true, web_used=false, memory_used=false. Daarmee is deze nieuwe kennis ook in de draaiende productiechat bevestigd, zonder een volledig modelregressietestpakket te claimen.

## Ronde 3 goedgekeurd en geselecteerd voor staging op 29 oktober 2026
- Dennis heeft de volledige verwerkte review expliciet goedgekeurd, inclusief de rode actualisaties van Mysteryland en Dominator, en opdracht gegeven deze naar staging te zetten. Geen gouden knop voor live ontvangen.
- Goedgekeurde verdieping over Mysteryland-locaties en de tijdlaag 2025/2026/2027, Dominator in Vlietland en als weekendfestival, Decibel-locaties, Ghosttown en Dance 2 Eden, Hellbound versus Hellraiser, Raving Nightmare versus A Nightmare in Rotterdam, Global Hardcore Nation, Operatie Staartjes en het gebruik van flyers en registraties geïntegreerd in ronde 3.
- Voor Mirko Kuit geldt de door Dennis bevestigde correctie: aanwezig bij editie II, maar geen publieke foto's gemaakt. De oude belofte dat hij bij editie II weer fotografeert is ook op de drie relevante plekken in de bestaande persona-kennis van ronde 7 gelijkgetrokken. Dit is geen volledige uitbreiding of herkeuring van ronde 7.
- Reviewvragen, blauwe commentaren en de formulering ter controle zijn niet als kennis naar de runtime gekopieerd. Bronverwijzingen en peildatum zijn behouden. De ontvangen Word blijft de reviewhistorie; de expliciete chatgoedkeuring rondt de laatste rode passages af.
- Alleen ronde 3, de beperkte consistentiecorrectie in ronde 7, de offline retrievaltest en deze statusbeschrijving worden op askyellow-staging/main gewijzigd. De kennisloader, drie-passagelimiet en het contextbudget blijven ongewijzigd.
- De bestaande negen retrievalchecks plus eenentwintig ronde-3-vragen en drie controles op conflicterende Mirko-formuleringen slagen met een verse snapshot van de stagingkennis: 33 checks, verdeeld over drie testmethoden. Dit is geen volledige modelregressietest of bewijs van de Render-deploy.
- Staging /health is vooraf bereikbaar met HTTP 200, env staging en db_ok true. Functionele controle van de nieuwe modelantwoorden volgt na de deploy.
- Productierepository askyellow-ai blijft in deze stap ongemoeid; ronde 3 wacht op stagingacceptatie en een afzonderlijke gouden knop.

## Reparatie vervolgvragen en bronselectie op staging
- Aanleiding: bij de vervolgvraag 'jo dus het is er nog steeds?' ging de oude code zonder Mysteryland zoeken en voegde ongerelateerde zoekresultaten automatisch als bronnen toe. Op 'dus dit jaar ook?' werd vervolgens onterecht een editie in 2026 bevestigd. Dennis gaf expliciet toestemming deze reparatie op staging uit te voeren; geen livegoedkeuring.
- Een begrensde onderwerpresolver gebruikt recente gesprekscontext en namen uit de goedgekeurde kennis. Historie bepaalt alleen waarnaar de vraag verwijst, nooit of een bewering waar is. Bij een onduidelijke of dubbele verwijzing volgt één gerichte vraag.
- De kennis wordt opnieuw geselecteerd met het opgeloste onderwerp; relatieve jaartallen volgen Europe/Amsterdam. Een onderwerpwissel mag geen oud jaar meenemen. De eerdere zwakke tekstmatch blokkeert deze herselectie niet meer.
- Algemene webresultaten krijgen een relevantiecontrole op titel en snippet, onderwerp, gevraagd jaar en waar relevant campinginformatie. Dit is een controle op zoekmetadata, geen volledige pagina- of entailmentverificatie. Een onderwerp alleen in een URL is onvoldoende. Ook een op datum passend resultaat over een ander genoemd festival wordt geweigerd.
- Alleen vooraf gefilterde bronnen waarnaar het model daadwerkelijk inline verwijst komen in de uiteindelijke bronnenlijst, met hernummering. Ontbrekende of ongeldige bronverwijzingen bij een webantwoord geven een eerlijke terugvaltekst; er wordt geen decoratieve bronnenlijst aangeplakt. Als een geselecteerde kennispassage het genoemde onderwerp en gevraagde jaar expliciet als overgeslagen benoemt, mag de terugval die gecontroleerde zin letterlijk gebruiken zonder webbronclaim. Deze terugval leidt geen positieve editie af en gebruikt geen chatbewering als bron.
- Bij een mislukte of lege webcheck mogen concrete gedateerde feiten uit de gecontroleerde kennis nog worden benoemd, maar niet als zojuist online bevestigd.
- Bestaande lokale agenda-zoekvragen en plaatscorrecties blijven ondersteund. Een genoemd festival blijft in een weekendzoekopdracht behouden; vandaag en morgen krijgen een concrete datum voor de bestaande datumfilter.
- Onderwerpselectie en bronfiltering zijn lokaal en vereisen geen extra modelaanroep. De bestaande kennisloader, maximaal drie kennispassages, het kennisbudget en de tokenlogging blijven behouden. Alleen bij een tijdgebonden vraag of vervolgvraag komt een korte extra onderwerpinstructie mee; algemene webcontext blijft op maximaal vier resultaten begrensd.
- 60 offline testmethoden slagen, inclusief de bestaande 33 kennischecks, de volledige gemelde gespreksketen met een vooraf fout assistentantwoord, onderwerpwissels, onbekende namen, dubbelzinnigheid, bronafwijzing, bronnummering, provideruitval, agenda-regressies, de expliciet gedateerde kennisterugval en overdracht van het onderwerp aan de modelprompt. Geen echte model- of provideraanroepen in deze offline tests.
- De eerste echte stagingproef vond nog onnodige dubbelzinnigheid: de intro Mysteryland in de jaren negentig maakte van de periode een tweede onderwerp. Periodes, kale jaartallen, getallen en stijlnamen zijn daarom als concurrerende namen uitgesloten. Twee extra regressietests dekken dit geval. De artiestenvervolgvraag over The Satan bleef in die praktijktest correct bij Rusland. De herhaalde volledige festivalproef volgt na deze naverbetering.
- De tweede praktijkproef hield het onderwerp vast en toonde geen ongerelateerde bronnen, maar de strenge citatiecontrole gaf een algemene terugvalzin ondanks de expliciete pauze in de kennis. De hierboven beschreven beperkte kennisterugval is daarom toegevoegd; de strenge broncontrole wordt niet losgelaten. De herhaalde praktijkproef moet ook bevestigen dat het antwoord over 2026 weer inhoudelijk bruikbaar is.
- Deze reparatie wordt uitsluitend op askyellow-staging/main gepubliceerd. Praktijktest na de Render-deploy volgt afzonderlijk; offline tests zijn geen garantie dat ieder modelantwoord correct is. Live blijft op bea850a5fedb031626fe8942481ea380ce5593b4 totdat Dennis afzonderlijk de gouden knop geeft.


## Gouden knop en kennisrelease ronde 3 op 30 oktober 2026
- Dennis heeft de stagingchat zelf gecontroleerd, is tevreden en heeft expliciet toestemming gegeven deel 3 naar main door te zetten.
- Productierepository askyellow-ai/main is bijgewerkt met de geaccepteerde ronde-3-kennis, de drie Mirko-consistentiecorrecties in ronde 7 en de bestaande offline retrievaltest. Releasecommit: 6a9a7ff9bb3b5c69d54d89f6e20f2d2797548e07. Vorige productiecommit: bea850a5fedb031626fe8942481ea380ce5593b4.
- De drie productieblobs zijn identiek aan stagingcommit 9181e234ebaed7db7ffd4fb24c8142490896425f. De vergelijking met de vorige productiecommit toont uitsluitend deze drie bestanden; main is na de overdracht opnieuw gecontroleerd.
- De kennisloader is op beide omgevingen identiek. De bestaande stagingtests zijn bij deze kennisoverdracht niet opnieuw uitgevoerd; dit verslag claimt geen nieuwe testuitslag.
- De latere wijzigingen aan chat.py, gabber_context.py, gabber_web.py en llm.py zijn niet onderdeel van deze beperkte kennisrelease en blijven op staging.
- De Render-deploy en een nieuw antwoord van de draaiende productiechat zijn vanuit deze sessie nog niet bevestigd.
- Deel 4 is als volgende kennisuitbreiding gestart vanuit de bestaande ronde-4-tekst. Nieuwe voorstellen en correcties blijven ter review; nog geen runtimepublicatie van deel 4.

## Volgende stappen
1. Ronde 1 en 2 afgerond: inhoud goedgekeurd, staging geaccepteerd, gouden knop ontvangen, livepromotie uitgevoerd en productieantwoord gecontroleerd.
2. Ronde 3 staat na de gouden knop op askyellow-ai/main; de draaiende productie nog onafhankelijk controleren. Ronde 4 uitbreiden op basis van de bestaande tekst en voorleggen ter review.
3. De tijdlaag in de overige rondes en operationele kennis nalopen voordat die worden gepubliceerd; deze publicaties corrigeren verwijzingen binnen ronde 2 en 3 en de expliciet bevestigde Mirko-zinnen in ronde 7.
4. Stagingwijzigingen uit de testsessie van september zijn hier niet opnieuw geïnspecteerd. Hun deploystatus en werking moeten vóór nieuwe implementatie worden vastgesteld; eerdere vermoedens over Render zijn geen bevestigde status.
5. Gerichte kennis- en gedragstests na integratie, gevolgd door expliciete livegoedkeuring.


## Reviewvoorbereiding ronde 4 op 30 oktober 2026
- Bestaande ronde-4-basis volledig behouden. Nieuwe verdieping en correctievoorstellen zijn als afzonderlijke rode aanvulling uitgewerkt, met tien bronverwijzingen en reviewvragen voor Dennis en Fer.
- Volledige leesversie: Gabber_Yello_Ronde_4_AANVULLINGEN_ROOD.html. Deze bevat de zwarte basis en rode voorstellen. De documentruntime kon niet worden geladen; er is daarom nog geen gerenderde en visueel gecontroleerde DOCX-versie geleverd.
- De ongedateerde Whitehouse-lockerprijs wordt uitsluitend als correctievoorstel behandeld; er is geen actuele prijs verzonnen. Geen ronde-4-inhoud naar de runtime gepubliceerd.


## Review ronde 4 ontvangen op 30 oktober 2026
- De zeven antwoorden van Dennis na de pijltjes zijn woordelijk en in blauw bij de bijbehorende vragen in de bestaande HTML-review bewaard.
- Cavello krijgt ook in de nieuwe verdieping een expliciete plek naast Australian. De beschrijving van de klassieke combinatie van kapsel, Aussie of Cavello en Air Max is als toegeschreven sceneherkenning verwerkt. Nieuwe formuleringen blijven rood tot hun eigen review.
- De correctie van de ongedateerde lockerprijs is expliciet goedgekeurd en zwart met gele markering weergegeven. Er is geen nieuwe actuele prijs vastgesteld.
- Geen extra pasjesnamen of dubbele armgebaren-uitleg toegevoegd. De bestaande brommer-uitleg blijft de verwijzing.
- Wens voor volgende fase vastgelegd: een echte hakkenworkshop die Gabber Yello kan geven. Die workshop is nog niet gebouwd en heeft nog geen uitgewerkt of goedgekeurd lesprogramma.
- Voorlopig geen nieuw familie- of reisverhaal. Dennis komt op mogelijke verdere wijzigingen in een volgende fase terug. Dit is geen onvoorwaardelijke goedkeuring van de volledige ronde en geen publicatieopdracht.
- Dennis deelde een positief testgesprek over Mysteryland en Mirko. De testomgeving is niet genoemd, zodat hiermee geen productie-deploy wordt bewezen. De stellige uitsluiting van een specifieke Mysteryland-band voor Mirko is als precisiepunt benoemd: ontbrekende bevestiging is geen bewijs dat zo'n band niet bestaat. Geen chatbotcode aangepast naar aanleiding van dit bericht.


## Ronde 4 goedgekeurd voor staging op 30 oktober 2026
- Dennis heeft de verwerkte ronde 4 expliciet volledig goedgekeurd en opdracht gegeven deze naar staging te zetten. Dit omvat de nieuwe Cavello-verdieping, de toegeschreven klassieke look en de lockerprijscorrectie. Geen liveopdracht.
- Alleen de goedgekeurde kennis is geselecteerd voor de runtime. De blauwe feedback, reviewvragen, redactionele voorstellen en toekomstige hakkenworkshop zijn niet meegepubliceerd. De oorspronkelijke reviewhistorie blijft bewaard.
- De ongedateerde lockerprijs is uit ronde 4 en de conflicterende praktische blokken partyinfo.json en whitehouse.json vervangen door de goedgekeurde verwijzing naar de informatie van de concrete editie. Er is geen nieuwe prijs of lockerlocatie ingevuld.
- De bestaande kennisloader, drie-passagelimiet en contextbudget blijven ongewijzigd. Eén kop in de nieuwe schoenverdieping noemt het concrete onderwerp expliciet zodat de bestaande kennisselectie de passage terugvindt.
- Op een geïsoleerde snapshot van de actuele stagingkennis zijn zes unittest-methoden geslaagd: 48 vraagcontroles voor rondes 1 tot en met 4 en lockers, plus controle dat ronde 4 geen reviewvragen of beloftes over de nog niet gebouwde workshop bevat. De tests gebruiken de echte bestaande kennisloader, zonder modelaanroepen, secrets of gesprekken.
- Deze publicatie wijzigt alleen ronde 4, de twee praktische kennisblokken, de bestaande retrievaltest en deze blueprint op askyellow-staging/main. askyellow-ai/live blijft ongewijzigd. Functionele controle na Render-deploy is niet door de offline tests bewezen.


## Gouden knop ronde 4 en bronreparaties op 30 oktober 2026
- Dennis heeft na zijn stagingcontrole expliciet opdracht gegeven ronde 4 naar main te zetten en de openstaande bronaanpassingen mee te nemen.
- Productierepository askyellow-ai/main staat op 6babe6264762ab864b8d2a51f97a9127a13ee06e. Vorige productiecommit voor gerichte rollback: 6a9a7ff9bb3b5c69d54d89f6e20f2d2797548e07. De branch is na publicatie opnieuw gecontroleerd.
- De release bevat ronde 4, de twee bijgewerkte praktische lockerblokken, bronroutering en citatiecontrole, de onderwerpresolver en de bijbehorende tests. In chat.py is uitsluitend de Gabber Yello-handler met noodzakelijke imports overgenomen. Alle dertien overige bestaande productiefuncties behouden hun oorspronkelijke AST. In llm.py zijn uitsluitend de onderwerp- en webcontextinstructies geïntegreerd.
- Voor publicatie zijn op de samengestelde productiesnapshot 63 unittest-methoden geslaagd, inclusief vervolgvragen, bronrelevantie, bronnummering, foutafhandeling, agenda-routing en de bestaande kenniscontroles. Vier gewijzigde Pythonmodules zijn ook syntactisch gecontroleerd. Geen echte model-, database- of provideroproepen in deze offline tests.
- GitHub meldt geen deploystatus voor de productiecommit. De draaiende Render-versie en een nieuw productieantwoord zijn in deze sessie nog niet onafhankelijk bevestigd.

## Ronde 5 voorbereid voor inhoudelijke review
- De actuele bestaande Markdown van ronde 5 is uit Library gelezen en volledig als zwarte basis behouden in Gabber_Yello_Ronde_5_AANVULLINGEN_ROOD.html.
- Nieuwe rode verdieping over white label versus testpersing en promo, heruitgaven, catalogusidentificatie en rollen, Mokum-bedrijfsgeschiedenis, concrete credits van DJ Chosen Few en DJ T-go, Industrial Strength-remixversies en de Top 40-notering van Kom Tie Dan Hè.
- Acht primaire bronpagina's zijn via de browser gecontroleerd op 30 oktober 2026. De webzoekfunctie gaf fouten; de broncontrole is daarom via de browser uitgevoerd. De DJ Norman-website was niet bereikbaar en is niet als opnieuw geverifieerde bron voor de nieuwe tekst gebruikt.
- Het DJ T-go-releasevoorbeeld bevestigt geen specifieke MHJH-agencyrelatie. De oorspronkelijke persingsdatum van Name Of The DJ wordt niet afgeleid uit de geraadpleegde remasteruitgave uit 2022.
- De rode voorstellen wachten op review door Dennis en Fer. Geen nieuwe ronde-5-inhoud naar staging of live gepubliceerd.

## Ronde 5 goedgekeurd en geselecteerd voor staging op 30 oktober 2026
- Dennis heeft de huidige ronde expliciet goedgekeurd en opdracht gegeven deze bij te werken en op staging te zetten. Geen liveopdracht.
- Zeven afzonderlijke reviewantwoorden en de twee afsluitende opmerkingen zijn woordelijk in blauw in dezelfde HTML-leesversie bewaard. Goedgekeurde aanvullingen zijn zwart met gele markering. De oude basis blijft reviewhistorie; de runtime vervangt de onjuiste gezamenlijke definitie en de te stellige catalogusnummerdefinitie.
- De goedgekeurde kennis bevat het onderscheid tussen testpersing, white label en promo; nuances bij heruitgaven, catalogusnummers en creditrollen; Mokum-geschiedenis; concrete versies en credits van MOK265 en MOK324; Industrial Strength-remixvoorbeelden; en de Top 40-gegevens van Kom Tie Dan Hè. Acht bronverwijzingen en de controledatum 30 oktober 2026 zijn behouden.
- Fers concrete lijst met aanvullende tracks en labels volgt later en is niet vooruit ingevuld. Voor deze ronde blijft de eigen MHJH-context beperkt tot Komt Tie Dan He en Den Haag Hakkûh. Er zijn geen persoonlijke plaatherinneringen van Dennis of Fer toegevoegd. De bestaande culturele conceptverwijzingen blijven behouden.
- De algemene goedkeuring omvat het huidige DJ T-go-releasevoorbeeld, maar bevestigt geen afzonderlijke agencyrelatie of overige persoonlijke band. De geraadpleegde MOK265-remasterdatum uit 2022 wordt niet als oorspronkelijke verschijningsdatum van Name Of The DJ gebruikt.
- Alleen de goedgekeurde inhoud is voor de runtime geselecteerd. Reviewvragen, blauwe antwoorden, redactionele voorstellen en de nog niet ontvangen tracklijst worden niet als kennis gepubliceerd.
- Op een verse geïsoleerde snapshot van de stagingkennis slagen acht unittest-methoden: 69 vraagcontroles over ronde 1 tot en met 5 en praktische lockerinfo, plus structurele controles op oude tegenstrijdigheden, reviewtekst en persoonlijke verhalen. De tests gebruiken de bestaande echte kennisloader, maximaal drie passages en hetzelfde contextbudget. Geen model-, database- of provideroproepen.
- Deze stagingpublicatie wijzigt uitsluitend het ronde-5-kennisbestand, de bestaande retrievaltest en deze blueprint. De loader en overige applicatiecode zijn ongewijzigd. Het Render-deployresultaat en echte modelantwoorden na deze publicatie zijn niet door de offline tests bewezen.
- Productierepository askyellow-ai/main wordt in deze ronde niet gewijzigd. Livepromotie wacht op Dennis' stagingcontrole en afzonderlijke gouden knop.

## Eerstvolgende stappen na de stagingpublicatie (stand vóór de gouden knop ronde 5)
1. Dennis en Fer controleren de bijgewerkte ronde 5 in de stagingchat.
2. Fers concrete tracklijst later ontvangen, gericht verifiëren en als nieuwe aanvulling voorleggen.
3. Alleen na afzonderlijke gouden knop de geaccepteerde ronde 5 naar askyellow-ai/main overzetten.
4. Daarna de volgende afgesproken kennisronde oppakken; persoonlijke herinneringen en de toekomstige hakkenworkshop niet zonder nieuwe inhoud invullen.


## Gouden knop ronde 5 op 30 oktober 2026
- Dennis heeft de huidige ronde 5 geaccepteerd, een testgesprek gedeeld en expliciet toestemming gegeven deze naar main te zetten en door te gaan naar ronde 6.
- Productierepository askyellow-ai/main staat op 309a2960060673d21bd4a518559df4a6dee43cc2. Vorige productiecommit voor een gerichte rollback: 6babe6264762ab864b8d2a51f97a9127a13ee06e. De branch is na publicatie opnieuw gelezen.
- De release wijzigt exact twee bestanden: de geaccepteerde ronde-5-kennis en tests/test_gabber_reviewed_rounds.py. Hun inhoud is identiek aan de geaccepteerde stagingcommit 35f9420c8ea56c78b2d288b7d44c967c52748f25. Geen overige applicatiecode, kennisloader of operationele informatie meegepromoveerd.
- De bestaande kenniscontroles zijn opnieuw uitgevoerd met de productie-loader en productiekennis, inclusief de afwijkende productieversies van lineup.json en tickets.json. Acht unittest-methoden met 69 vraagcontroles en structurele controles slagen. Dit zijn offline tests zonder echte model-, database- of provideroproepen.
- Render is vervolgens rechtstreeks gecontroleerd. Het dashboard noemt commit 309a2960060673d21bd4a518559df4a6dee43cc2 als Last successfully deployed commit en toont Live. Deploydetail: https://dashboard.render.com/web/srv-d46atckhg0os73ef6ct0/deploys/dep-dbicp7g473hc73f0gd50. Daarmee is deze deployment bevestigd; geen nieuwe productie-modelantwoorden onafhankelijk getest.
- Het gedeelde testgesprek bevat verbeterpunten: classics worden te gemakkelijk als white labels bevestigd; concrete persingen en een genoemde trackcredit worden niet onderbouwd; vinylvoorkeur wordt als algemene technische superioriteit verwoord; hardstyle wordt zonder nuance in een lijst hardcoresubgenres gezet. Deze uitingen zijn testmateriaal, geen nieuw goedgekeurde feiten.
- De livepromotie verandert alleen de al goedgekeurde ronde 5. De nieuwe correctievoorstellen zijn herkenbaar rood in ronde 6 opgenomen en wachten op review. Fers tracklijst is nog niet ontvangen.

## Ronde 6 voorbereid voor inhoudelijke review
- De actuele volledige Library-basis Gabber_Yello_Hardcorekennis_Ronde_6_Termen_en_Dubbele_Betekenissen.md is gelezen en zwart behouden in Gabber_Yello_Ronde_6_AANVULLINGEN_ROOD.html.
- Veertien nieuwe rode onderdelen verdiepen contextwissels, de taalherkomst van gabber, white label versus classics, bootleggebruik, BPM/pitch, beatmatching/sync, cue, beatgrid, DVS, stems, clipping/headroom, releasecredits, vinylvoorkeur en vriendelijk corrigeren. De aanvulling bevat acht bronnen en zeven gerichte reviewvragen.
- Acht bronpagina's zijn via de browser gelezen op 30 oktober 2026: Etymologiebank/EWN, twee Discogs-richtlijnen, Ableton en drie Mixxx-handleidingpagina's plus de Native Instruments-Stems-pagina. De webzoekfunctie gaf een fout. Technische handleidingen worden gebruikt voor hun eigen techniek, niet als gezag over een officiële gabbernorm.
- De koppeling The Speed Freak — The Ultimate Seduction uit het testgesprek is niet als geverifieerd releasefeit opgenomen. Het concrete voorbeeld wacht op vaststelling van de bedoelde uitgave; er wordt geen vervangende artiest gegokt.
- Het aangeleverde testgesprek is als aparte blauwe bewaartekst toegevoegd en nadrukkelijk als ongeverifieerd testmateriaal gemarkeerd. Geen persoonlijke herinneringen van Dennis of Fer verzonnen.
- HTML-structuur, kleurregels, bronlinks, aanwezigheid van de volledige basis en het ontbreken van uitvoerbare scripts zijn gecontroleerd. Een lokale browserweergave was door het URL-beleid geblokkeerd; de pagina is daarom niet visueel in de browser gekeurd. Er is geen DOCX-render geclaimd.
- Ronde 6 is uitsluitend een reviewdocument. Geen nieuwe ronde-6-kennis of gespreksregels op staging of live gezet.

## Actuele vervolgstappen
1. Dennis en Fer lezen ronde 6 en geven feedback; voorstellen rood, antwoorden blauw, goedkeuring later geel verwerken.
2. Fers concrete lijst met tracks en labels later gericht controleren en als afzonderlijke aanvulling voorleggen.
3. Na inhoudelijk akkoord de geselecteerde ronde-6-kennis naar staging, gericht testen en vervolgens wachten op afzonderlijke gouden knop voor live.
4. Ronde 7 en de toekomstige hakkenworkshop blijven latere fasen. Geen voorkeuren, persoonlijke verhalen of workshopinhoud vooruit invullen.

## Ronde 6 goedgekeurd voor staging op 30 oktober 2026
- Dennis heeft de volledige ronde 6 doorgenomen, zeven reviewantwoorden gegeven en expliciet opdracht gegeven deze naar staging te zetten. Geen liveopdracht.
- De zeven antwoorden en de afsluitende publicatieopdracht zijn woordelijk in blauw in dezelfde HTML-review bewaard. Goedgekeurde aanvullingen staan zwart met gele markering. De bestaande zwarte basis en het eerdere blauwe testgesprek blijven reviewhistorie.
- De kanttekening bij cue, beatgrid, sync, DVS en stems is verwerkt: gewone taal als uitgangspunt, vaktermen alleen wanneer relevant of gevraagd, een noodzakelijke term bij eerste gebruik kort uitleggen en geen dj- of productiekennis veronderstellen. De technische onderdelen dragen dezelfde begrenzing.
- De goedgekeurde contextregels, taalherkomst van gabber, white-labelcorrectie, bootlegnuance, BPM/pitch-uitleg, technische definities, releasecreditregels, vinylvoorkeur en vriendelijk corrigeren zijn geselecteerd voor de runtime. De oude white-labeltabel en de te algemene contextvoorrang zijn daarmee gelijkgetrokken.
- Geen nieuwe Haagse woorden toegevoegd; de bestaande uitleg blijft behouden. Fers concrete tracklijst volgt later. Geen persoonlijke herinneringen of toekomstige hakkenworkshop ingevuld.
- Reviewvragen, blauwe reacties, het oude testgesprek en de ongeverifieerde Speed Freak-titelkoppeling staan niet in de runtime. De kennis bevat algemene regels om onbevestigde credits niet te herhalen.
- Twee inhoudelijk beschrijvende koppen zijn voor de bestaande selectie verduidelijkt: de bootlegpassage in ronde 6 en de bestaande kop bij catalogusnummer/matrixnummer in ronde 5. Bij ronde 5 verandert alleen die kop; de eerder goedgekeurde uitleg blijft inhoudelijk gelijk.
- Op een met de actuele stagingtree vergeleken kennissnapshot slagen tien unittest-methoden met 89 vraagcontroles voor ronde 1 tot en met 6 en de praktische lockerinfo, plus structurele controles. De tests gebruiken de echte ongewijzigde kennisloader, maximaal drie passages en hetzelfde contextbudget; geen model-, provider- of databaseaanroepen.
- De stagingpublicatie wijzigt ronde 6, de ene ronde-5-kop, de bestaande retrievaltest en deze blueprint. Geen overige applicatiecode of secrets gewijzigd. Offline tests bevestigen geen echte modelantwoorden of Render-deploy.
- Productierepository askyellow-ai/main blijft in deze stap ongemoeid; livepromotie wacht op Dennis' stagingcontrole en afzonderlijke gouden knop.

## Actuele vervolgstappen na goedkeuring ronde 6
1. De nieuwe ronde 6 in de stagingchat controleren, met extra aandacht voor gewone taal bij vaktermen.
2. Na afzonderlijke gouden knop de geaccepteerde stagingkennis gecontroleerd naar askyellow-ai/main overzetten.
3. Fers concrete tracklijst later verifiëren en als aanvulling voorleggen.
4. Ronde 7 en de hakkenworkshop blijven latere fasen; geen inhoud of voorkeuren vooruit invullen.


## Bijschaven MHJH, feestnamen en tracknamen op staging
- Dennis meldde een productiegesprek waarin Kom Tie Dan Hè!, de MHJH-feestnaam en Den Haag Hakkûh niet concreet werden onderscheiden. De bot herhaalde een vage culturele verwijzing en deed een ongefundeerde negatieve rechtenclaim. Er is in dit bericht geen gouden knop voor ronde 6 of deze reparatie gegeven.
- De eigen eerdere formuleringen van Dennis zijn via Personal Context teruggevonden: MHJH Events is de organisator van het feest/concept Komt Tie Dan He – Den Haag Hakkûh; Den Haag Hakkûh II is de tweede editie. Geen nieuwe overkoepelende/submerkhiërarchie afgeleid.
- De expliciete naamcontext noemt organisator, feesttitel en afzonderlijke tracks. De oude geforceerde aanname dat iedere vraag over Den Haag Hakkûh een verwarring tussen 1993 en 2023 is, is vervangen door de relevante relaties en de instructie de huidige vraag te beantwoorden.
- Korte verduidelijkingsvragen zoals 'die snap ik niet kun je dat beter uitleggen' krijgen deze context alleen wanneer een recente gebruikersvraag het onderwerp al benoemde. De laatste acht berichten begrenzen de context; een onderwerpwissel stopt de overdracht en een assistentbewering is geen feitenbron of zelfstandig naamanker.
- In chat.py is alleen de bestaande kennisaanroep in gabber_yello_chat uitgebreid met de reeds opgehaalde historie. Alle veertien overige functies behouden hun oorspronkelijke AST. Er komt geen extra modelaanroep, databasequery of internetzoekactie voor deze naamcontext bij.
- De bestaande MHJH-kennis en ronde-5-passage zijn gelijkgetrokken: eerst uitleggen wie het feest organiseert en hoe het heet; pas waar relevant de culturele verwijzing naar de plaat. Geen positief of negatief oordeel over MHJH-rechten, licenties, toestemming, contracten of labelrol afleiden uit artiestcredits. Geen algemene uitspraak dat MHJH nooit tracks of anthems uitbrengt.
- De officiële Top 40-pagina is opnieuw via de browser gelezen op 30 oktober 2026: 2005, piekpositie 4, acht weken totaal. De kennis en naamcontext verbieden daaruit een aantal weken op positie 4 af te leiden. Bron: https://www.top40.nl/dj-norman-vs-darkraver/dj-norman-vs-darkraver-kom-tie-dan-he-9352.
- 74 offline unittest-methoden slagen, inclusief de volledige gemelde keten aan de echte handler/modelgrens met gemockte diensten, begrensde vervolgcontext, onderwerpwissels, bronfiltering, agenda-regressies en de 89 bestaande kennisvraagcontroles. Twee gewijzigde Pythonbestanden zijn syntactisch gecontroleerd. Dit bewijst geen daadwerkelijke modelantwoorden.
- De publicatie blijft beperkt tot askyellow-staging/main: core/mhjh_context.py, de ene aanroep in chat.py, mhjh.json, de gerichte ronde-5-verduidelijkingen, een nieuwe regressietest en deze blueprint. Productie blijft op 309a2960060673d21bd4a518559df4a6dee43cc2.
- De bestaande inhoudelijke goedkeuring van ronde 6 en de inzet van gewone taal bij vaktermen blijven behouden. Deze reparatie is een aparte stagingverbetering; ronde 7 is nog niet gestart.


## Praktijkproef en afronding naamreparatie
- Render heeft stagingcommit fc2b148d6b31f2eb0596f6a62756404e75208aeb succesvol gedeployed. De volledige gemelde keten is daarna via de staging-API met een nieuwe geïsoleerde gast-sessie getest. Alle vijf antwoorden gebruikten kennis, zonder webbronnen of accountherkenning.
- De echte antwoorden benoemden MHJH Events als organisator, Komt Tie Dan He – Den Haag Hakkûh als feesttitel en de track uit 2005 apart. De laatste verduidelijking bevestigde Den Haag Hakkûh als deel van de feestnaam. De fout over vier weken op nummer 4 en de ongefundeerde negatieve rechtenclaim kwamen niet terug.
- De proef maakte nog een onjuiste afkortinguitleg zichtbaar: MHJH werd uitgelegd als MHJH Events. De naamcontext noemt daarom nu ook expliciet Mijn Huis Jouw Huis. Bij herhaald onbegrip krijgt de assistent de instructie maximaal drie korte concrete zinnen te gebruiken.
- Na deze naverbetering slagen dezelfde 74 offline testmethoden. De herhaalde praktijkproef volgt na de nieuwe stagingdeploy; een model kan nog steeds variëren in formulering. Main is niet gewijzigd.

## Gouden knop ronde 6 en naamreparatie op 30 oktober 2026
- Dennis heeft expliciet de gouden knop gegeven: de geaccepteerde ronde 6 en de MHJH-naamreparatie mogen naar main.
- Productierepository askyellow-ai/main is gecontroleerd bijgewerkt naar 36b44b58b1388de48f543a283e948f64efc0231b. Vorige productiecommit voor een gerichte rollback: 309a2960060673d21bd4a518559df4a6dee43cc2.
- De release wijzigt precies zeven bestanden: core/mhjh_context.py, de ene kennisaanroep in chat.py, mhjh.json, de gerichte ronde-5-verduidelijkingen, ronde 6 en de twee bijbehorende tests. De zes overgenomen bestanden zijn byte-identiek aan stagingcommit 662be561dd22ea0c52318ab84f02a6789c941e6a. In chat.py is uitsluitend de history-parameter toegevoegd aan de bestaande kennisaanroep; de overige veertien functies behouden hun productie-AST.
- De afwijkende liveversies van lineup.json, tickets.json en llm.py blijven behouden. Geen overige stagingcode, operationele informatie, databasewijzigingen of secrets meegepromoveerd.
- De kandidaat is getest met de productiecode en productiekennis als basis: 74 offline unittest-methoden slagen, inclusief de 89 bestaande kennisvraagcontroles en de volledige gemelde naamketen aan de handler/modelgrens met gemockte diensten. Geen echte model-, database- of provideroproepen in deze tests.
- De tweede echte stagingproef na deploy van 662be561dd22ea0c52318ab84f02a6789c941e6a gaf vijf antwoorden die organisator, volledige feesttitel en afzonderlijke tracks uit elkaar hielden, zonder de ongefundeerde rechtenclaim of verwarring over weken op piekpositie. De formulering bleef bij herhaald onbegrip soms uitvoeriger dan gevraagd.

- Render heeft releasecommit 36b44b58b1388de48f543a283e948f64efc0231b succesvol gedeployed en toont Deploy succeeded|Live, duur 1m03s. Deploydetail: https://dashboard.render.com/web/srv-d46atckhg0os73ef6ct0/deploys/dep-dbidfan40ujc739b0oa0.
- Daarna is de volledige gemelde keten via https://askyellow-ai.onrender.com/gabber-yello/chat in een nieuwe geïsoleerde gast-sessie getest. Alle vijf antwoorden gebruikten kennis, zonder webbronnen of accountherkenning. De eerste beurt gaf piekpositie 4 en acht weken totaal correct; de derde en vierde beurt onderscheiden de track van het feest en noemen MHJH als organisator. De ongefundeerde rechtenclaim kwam niet terug.
- Restpunt uit deze productieproef: de tweede beurt herhaalde nog een vage culturele verwijzing; de laatste beurt gebruikte concept en evenement nog onnodig als verschillende labels en gaf de volledige gezamenlijke titel niet opnieuw. De vierde beurt noemde de volledige feesttitel wel correct. De release en deploy zijn bevestigd; deze proef is geen bewijs dat de formulering in ieder modelantwoord is opgelost.
- De expliciete MHJH-context, de ronde-6-regels voor gewone taal en de nieuwe regressietests zijn nu live. Fers tracklijst is nog niet ontvangen. Ronde 7 en de toekomstige hakkenworkshop blijven afzonderlijke volgende fasen.

## Actuele vervolgstappen na livegang ronde 6
1. Het resterende formuleringgedrag rond de volledige feesttitel gericht evalueren bij verdere chatcontrole; geen volledige oplossing claimen op basis van alleen prompt- of offline tests.
2. Fers concrete tracklijst later ontvangen en de bedoelde releases en versies verifiëren.
3. Ronde 7 of de hakkenworkshop pas uitwerken wanneer die fase wordt opgepakt; geen persoonlijke voorkeuren of verhalen invullen.


## Ronde 7 beoordeeld en geselecteerd voor staging op 1 november 2026
- Dennis heeft de laatste van de zeven kennisrondes volledig doorgenomen, acht reviewantwoorden gegeven en daarna expliciet opdracht gegeven de verwerkte ronde naar staging te zetten. Geen gouden knop voor productie.
- De volledige leesversie Gabber_Yello_Ronde_7_AANVULLINGEN_ROOD.html bevat de bestaande basis, veertien inhoudelijk goedgekeurde aanvullingen in zwart met geel en alle acht antwoorden woordelijk in blauw. Het bestand is inmiddels duurzaam opgeslagen als libfile_0dbf051843a881919a304ec99504eac1. De eerdere voorbereiding en opslagbeperking zijn hiermee voor deze leesversie ingehaald; de oorspronkelijke lokale reviewversie blijft bewaard.
- Early is bevestigd als vertrekpunt, terwijl Yello met elke stijl mee moet kunnen komen. De artiesten- en trackvoorbeelden worden later met Fers concrete lijst verfijnd; er is geen nieuwe vaste ranglijst of persoonlijke plaatherinnering toegevoegd.
- De bijlgrap wordt geen automatische afsluitzin of losse standaardcallback. Humor blijft afhankelijk van de context. Dennis en Fer mogen als bron of kenniscontroleur genoemd worden uitsluitend wanneer de herkomst van de specifieke kennis daadwerkelijk vaststaat; geen algemeen bronlabel op onbekende of anders afkomstige kennis.
- De goedgekeurde aanvullingen over digitale identiteit, onderbouwde smaak, warm maar feitelijk begrensd reageren, organisator/feest/track, herformuleren, gewone taal, humor, klachten, historische programmering, Mirko/foto's, herkenning en bronattributie zijn voor de runtime geselecteerd. Reviewvragen, blauwe antwoorden, redactionele sjablonen en placeholders zijn uitgesloten.
- De bestaande ronde-7-passages zijn op de relevante plaatsen gelijkgetrokken: geen Mirko-camera-belofte, geen vaste bijlcallback, editie II als historische programmering en de bestaande tracklijst als voorbeelden in afwachting van verfijning. De bij ronde 3 goedgekeurde Mirko-correcties blijven behouden.
- Twee oudere actieve instructies botsten met de review: het absolute verbod op een gecontroleerd trackvoorbeeld bij smaakvragen en het vooraf aannemen van Haagse titelverwarring. Die zijn begrensd herformuleerd volgens het inhoudelijke akkoord. Een keuze op criterium mag uit aangeleverde gecontroleerde kennis; verzonnen vaste favorieten of ontbrekende credits blijven verboden.
- De kernregels uit ronde 7 zijn compact in GABBER_YELLO_PROFILE verwerkt, zodat ze niet afhankelijk zijn van toevallige passage-selectie. Het YellowMind-profiel blijft exact gelijk. Geen nieuwe modelaanroep, databasequery, webzoekactie of antwoordfilter toegevoegd; het vaste Gabber-profiel is wel iets langer. De bestaande selectie van maximaal drie passages en het kennisbudget blijven ongewijzigd.
- Op een met de actuele stagingtree vergeleken snapshot slagen 80 offline unittest-methoden: de bestaande 74 plus zes ronde-7-tests op kennisselectie, afwezigheid van reviewtekst, het daadwerkelijke modelaanroep-pad met gemockte diensten, voorwaardelijke bronattributie en behoud van YellowMind. De bestaande 89 kennisvraagcontroles blijven slagen. Twee gewijzigde Pythonmodules zijn syntactisch gecontroleerd. Deze tests doen geen echte provider-, model- of databaseoproepen.
- De stagingpublicatie omvat uitsluitend het ronde-7-kennisbestand, core/personalities.py, de gerichte favorietregel in core/mhjh_context.py, tests/test_gabber_round7_persona.py en deze blueprint. De runtime en productierepository askyellow-ai/main blijven op hun bestaande productieversie totdat Dennis afzonderlijk de gouden knop geeft.
- De Render-deploy en echte chatproef volgen na de publicatie. Fers lijst en de toekomstige hakkenworkshop blijven aparte vervolgfasen.

## Actuele vervolgstappen na selectie ronde 7
1. De Render-stagingdeploy bevestigen en smaak, humor, bronattributie en de naamrelatie in echte gastchats controleren.
2. Dennis en Fer testen de stagingchat en geven eventuele resterende opmerkingen.
3. Alleen na een afzonderlijke gouden knop de geaccepteerde ronde 7 gecontroleerd naar productie overzetten.
4. Fers concrete tracklijst later ontvangen en verifiëren; geen releasecredits of workshopinhoud vooruit invullen.

## Eerste echte ronde-7-proef en naverbetering
- Render heeft stagingcommit a2142e7141122082352e1b9f99dbe6a5165ecca1 succesvol gedeployed (1m16s). Acht vragen zijn daarna in vier geïsoleerde gastgesprekken getest. Uptempo werd inhoudelijk besproken, de eerste-feesttip kreeg geen bijlgrap, bronattributie bleef voorwaardelijk, Mirko kreeg de concrete Dennis-bevestiging en organisator/feesttitel/track werden onderscheiden. De uitleg bleef soms langer dan gevraagd en bevatte nog een automatische vervolgvraag.
- Op “Wat vind jij de beste track?” noemde het model een niet door de geselecteerde kennis ondersteund artiest-titelpaar. De smaakvangrail herkende vooral favoriet, niet beste track. De bestaande vangrail is daarom uitgebreid met de beste-track-/nummer-/plaat-/artiest-vraag aan Yello en een expliciete instructie geen titel te noemen als een gecontroleerd artiest-titelpaar ontbreekt. Dit voegt geen nieuwe trackcredit toe.
- Na deze naverbetering slagen dezelfde 80 offline testmethoden, met extra vraagvarianten binnen de bestaande smaaktest. De nieuwe deploy en herhaalde smaakproef volgen; het eerste ongecontroleerde voorbeeld wordt niet als bronfeit overgenomen.

## Aanvullende begrenzing na de tweede echte smaakproef
- De herhaalde proef na succesvolle deploy van 25cb9b6d8b44427022c8c3a5d6bec2138fef5cd4 noemde opnieuw een niet door de geselecteerde kennis ondersteund trackvoorbeeld. Alleen promptaanscherping bleek voor deze vraag onvoldoende. Geen van beide proefvoorbeelden is als nieuwe kennis of credit opgenomen.
- Daarom heeft uitsluitend de Gabber-wrapper in llm.py een begrensde terugval voor persoonlijke favoriet-/beste-trackvragen met het bestaande smaakanker en zonder concreet gecontroleerd artiest-titelpaar in de geselecteerde kennis. De terugval noemt muzikale criteria zonder tracknaam en doet geen modelaanroep. Wanneer een gecontroleerd paar in de bestaande lijstvorm is geselecteerd, blijft de gewone modelroute beschikbaar. YellowMind en alle overige vragen houden hun bestaande route. Dit is geen algemene releasecreditvalidator.
- 81 offline unittest-methoden slagen, inclusief de nieuwe wrappercontrole die bevestigt dat een ontbrekend gecontroleerd paar geen modelaanroep krijgt en een geselecteerd concreet paar de modelroute beschikbaar houdt. Syntax en de bestaande 89 kennisvraagcontroles blijven goed. De uiteindelijke stagingrelease bevat daarom ook deze gerichte wijziging aan llm.py: zes bestanden in totaal.


## Bevestigde stagingstand ronde 7
- Definitieve stagingcommit: 4bad67b69598b1640d0a868416bb28fd6e296a02, op askyellow-staging/main. Render bevestigt Deploy succeeded|Live, duur 1m09s. Deploydetail: https://dashboard.render.com/web/srv-d4et0ne3jp1c738nklcg/deploys/dep-dbjk99vavr4c73c56p40.
- De uiteindelijke vergelijking met 662be561dd22ea0c52318ab84f02a6789c941e6a toont uitsluitend zes bedoelde bestanden: core/mhjh_context.py, core/personalities.py, llm.py, het ronde-7-kennisbestand, de nieuwe ronde-7-test en deze Git-blueprint. Bestaande regelafbrekingen zijn behouden. De selectie- en scoringsfuncties van de kennisloader zijn ook per AST gelijk gebleven; alleen de bestaande disambiguatie-/smaakregel veranderde.
- Na deze laatste deploy is de stijl-/smaakketen in een nieuwe gastchat herhaald. Uptempo werd besproken zonder de bezoeker terug naar early te trekken. Op “Wat vind jij de beste track?” kwam nu de begrensde reactie: “Een vaste nummer één heb ik niet. Voor mij telt vooral een eigen sound, een goede opbouw en de juiste plaat op het juiste moment in de set.” Er werd geen onbevestigd artiest-titelpaar ingevuld.
- Samen met de eerdere acht-vragenproef bevestigt dit de gecontroleerde werking van de beoogde cases. Het is geen garantie dat ieder modelantwoord kort of foutloos is. De eerste proef bevatte nog een automatische vervolgvraag en een soms langere uitleg; die stijlpunten blijven aandachtspunten bij Dennis' stagingcontrole.
- Productie is opnieuw gelezen en staat nog op 36b44b58b1388de48f543a283e948f64efc0231b. Geen productiepromotie uitgevoerd. De gouden knop voor ronde 7 is nog niet gegeven.
- Alle zeven thema’s zijn nu inhoudelijk behandeld. Ronde 7 staat ter praktijktest op staging. De concrete tracklijst van Fer en de hakkenworkshop blijven afzonderlijke vervolgstappen.


## Reparatie onbekende personen in verjaardagsverhalen op staging — 1 november 2026
- Dennis deelde een fout gesprek: een onbekende, klein geschreven naam in een verjaardagsverhaal werd zonder bron een goede naam in de scene genoemd. Op de vervolgvraag gaf Yello aan de persoon niet te kunnen plaatsen, maar herhaalde de onbewezen reputatieclaim alsnog. Dit testgesprek is geen nieuwe feitenbron over Dabudda.
- De oude naamwaarschuwing herkende vooral hoofdletters. Een begrensde herkenning voor expliciete verwijzingen zoals verjaardag (gehad) van, ken je en wie is werkt nu ook bij kleine letters en korte samengestelde namen. Gewone woorden en bekende namen worden niet automatisch als onbekende persoon behandeld.
- Voor deze expliciet genoemde personen worden uitsluitend de lokaal gecontroleerde kennisbestanden als bron gebruikt. De naamindex is gecachet. Gespreksgeschiedenis wordt niet als feitenbron geïndexeerd; de meest recente gebruikersverwijzing mag alleen een korte verwijzing zoals hem oplossen. Een onderwerpwissel stopt die overdracht.
- De Gabber-wrapper heeft een gerichte, modelvrije reactie op een eenvoudig positief verjaardagsverhaal met een onbevestigde naam: aansluiten op wat de gebruiker zelf vertelde, zonder bekende dj, reputatie, sceneverband of nieuwe feestdetails toe te voegen. Bij een directe identiteitsvraag benoemt Yello dat hij de naam niet betrouwbaar kan plaatsen. Een recente eigen onbewezen reputatieclaim wordt kort ingetrokken in plaats van als onderbouwing herhaald.
- Hulpvragen, concrete signalen van nood, negatieve verhalen en inhoudelijke vragen over het feest vallen niet onder deze eenvoudige verjaardagsreactie en houden de normale assistentroute. De wijziging is bewust geen algemene persoonsherkenner en bevestigt of ontkent niet wie Dabudda in werkelijkheid is.
- De algemene persona-instructie is gelijkgetrokken: enthousiasme bij een persoonlijk verhaal is geen bewijs van bekendheid, ook niet wanneer het model die bekendheid eerder zelf claimde. Geen nieuwe persoonsfeiten, feestdata, credits of privéverhalen aan de kennisbank toegevoegd.
- 90 offline unittest-methoden slagen: de bestaande 81 plus negen controles voor de gemelde keten, oude foutclaims in de historie, kleine/hoofdletters en meerwoordnamen, bekende personen en gewone vragen, begrensde gebruikersverwijzingen, bronuitsluiting van chatclaims, de echte Gabber-wrapper met gemockte modeldienst en behoud van de normale hulproute. Geen echte model-, provider- of databaseoproepen in deze tests.
- De echte eerste zin is ook vóór de reparatie in een aparte gast-sessie geprobeerd. Daar kwam deze keer geen reputatieclaim uit, wel een generieke vervolgvraag. De gemelde fout is dus niet als elke keer reproduceerbaar opgevoerd; de offline regressie bevat expliciet de door Dennis gedeelde oude foutclaim.
- De stagingreparatie wijzigt uitsluitend core/mhjh_context.py, core/personalities.py, llm.py, tests/test_gabber_unknown_people.py en deze blueprint. Kennisselectie, drie-passagelimiet en kennisbudget blijven behouden. Er komen geen extra modelaanroepen of databasequeries bij; de begrensde terugval slaat juist een modelaanroep over.
- Productie blijft op 36b44b58b1388de48f543a283e948f64efc0231b. Geen gouden knop of productiepromotie. Render-deploy en echte nameting volgen na publicatie.

## Bevestigde stagingreparatie onbekende personen
- Stagingcommit a1c6824cd029c38baa20e4f4f00dcd82e805cc0b is succesvol gedeployed door Render (Live, 1m22s): https://dashboard.render.com/web/srv-d4et0ne3jp1c738nklcg/deploys/dep-dbjkir7b9u1s73bqcfi0.
- De echte gerapporteerde keten is na de deploy in een nieuwe gastchat getest. Eerste antwoord: “Klinkt gezellig, maat! Mooi dat je een leuke avond hebt gehad.” Daarna op “ja? ken je dabudda?”: “Ik kan Dabudda niet betrouwbaar plaatsen.” De extra verwijzing “Ken je hem?” geeft dezelfde begrensde reactie.
- Ook de gastchat van vóór de reparatie geeft bij de identiteitsvraag de begrensde reactie. Een aparte vraag over Darkraver blijft via de normale modelroute inhoudelijk beantwoord. In totaal vijf succesvolle echte nametingen. Het intrekken van de gemelde oude reputatieclaim is offline met die concrete gespreksgeschiedenis getest; die foutclaim is niet kunstmatig in een live chat geïnjecteerd.
- Alle 90 offline tests waren vóór publicatie groen. Productie/main is na de stagingdeploy opnieuw gelezen en staat nog op 36b44b58b1388de48f543a283e948f64efc0231b. De wijziging staat klaar voor Dennis’ praktijktest; geen promotie naar productie uitgevoerd.

## DaBuddha en Bridgeway Records — toevoeging op verzoek van Dennis, 1 november 2026
- Dennis vroeg na de onbekende-persoonreparatie expliciet DaBuddha aan de artiestenkennis en Bridgeway Records aan de labelkennis toe te voegen. Deze gerichte toevoeging wordt op staging uitgevoerd; geen gouden knop voor productie.
- DaBuddha / Da Buddha / Daniel Gouweleeuw: Nederlandse dj en entertainer; hardstyle, raw hardstyle, freestyle en hardcore. De chatspelling dabudda is als herkenningsvariant opgenomen. Real Hardstyle geeft de eigen biografische tekst over het opnieuw draaien/streamen vanaf november 2021; dit is geen beginjaar van zijn hele sceneloopbaan. Beide aangeleverde Partyflock-profielen noemen dezelfde burgerlijke naam en website. Geen geboortedatum, vaste leeftijd, actuele agenda of streambelofte vastgelegd.
- De opvolging van Mirko Kuit als officieel Thunderdome-fotograaf komt rechtstreeks van Dennis en wordt op zijn expliciete verzoek als toegeschreven MHJH-inside-informatie opgenomen: “Volgens Dennis van MHJH heeft DaBuddha het stokje van Mirko Kuit overgenomen als officieel fotograaf van Thunderdome.” De openbare dj-profielen onderbouwen deze specifieke opvolging niet. Geen beginjaar, exclusiviteit of contractdetails ingevuld.
- Bridgeway Records: platenlabel, opnamestudio en dj-platform in Waddinxveen, met livesets/mixtapes en verschillende stijlen. Eigen SoundCloud-zelfomschrijving en setpublicaties plus de portfolio van audiobrandingmaker Mark Koster ondersteunen de kaart. Labelrelease en gepubliceerde dj-set blijven onderscheiden. Gratis opnames, een vaste opnameduur en een actueel uitzendschema zijn niet als blijvende belofte overgenomen. Instagram en het YouTube-kanaal konden niet zelfstandig worden uitgelezen; geen inhoud daaruit als gecontroleerd opgevoerd. Bronlinks en peildatum staan bij beide kenniskaarten.
- De bestaande onbekende-persoonvangrail blijft actief voor werkelijk ongecontroleerde namen. De negen generieke tests gebruiken daarom nu een fictieve naam in plaats van de inmiddels gecontroleerde DaBuddha. Drie nieuwe tests controleren vijf naamvarianten, daadwerkelijke overdracht aan de bestaande Gabber-wrapper, bronattributie van de fotograafpassage en de scheiding tussen Bridgeway-livesets en labelreleases.
- Een concrete selectietest liet zien dat de fotograafpassage bij een gecombineerde DaBuddha/Mirko/Thunderdome-vraag kon wegvallen. De sectietitel noemt nu die personen en Thunderdome zodat de bestaande selectie haar vindt; geen scoringsfunctie, passage-aantal of kennisbudget gewijzigd. Ken en kennen zijn toegevoegd aan de bestaande lijst gewone woorden die geen persoonsnaam vormen, zodat “Ken je Bridgeway Records?” geen waarschuwing voor de naam Ken oproept.
- 93 offline unittest-methoden slagen met de actuele stagingbasis. De drie nieuwe tests controleren relevante selectie en de echte wrapper met gemockte modeldienst; geen echte model- of databaseoproepen in deze tests. De gewijzigde runtimebestanden zijn alleen de twee kenniskaarten en twee woorden in NAME_IGNORE. Verder wijzigen de generieke onbekende-naamtest, de nieuwe kennisselectietest en deze blueprint: zes bestanden totaal.
- Render-deploy en echte stagingproef volgen na publicatie. Productie blijft voor deze stap ongemoeid.

## Eerste echte proef en aanscherping van bronattributie
- Render bevestigde commit 1626371060db35929072effc4d671c8943017324 als Live (1m15s). Zes echte stagingvragen bevestigden herkenning van DaBuddha, Bridgeway als label/studio/platform en het onderscheid tussen liveset en labelrelease. Een fictieve onbekende naam bleef begrensd.
- De fotograafantwoorden lieten de expliciete bron Dennis weg en één antwoord vulde recentelijk in. Dit wordt niet als geslaagde bronattributie opgevoerd. Daarom is de bestaande MHJH-instructie in call_yello_llm aangevuld: de specifieke bron blijft in dezelfde zin verplicht, ook bij herhalen; inside-informatie wordt niet door beheer van het kennisblok onafhankelijk openbaar bewijs; geen ongegeven actualiteit, startjaar of exclusiviteit. Geen extra modelaanroep of nieuwe persoonsfeiten.
- Een vierde nieuwe test controleert deze eis aan de echte modelpromptgrens met gemockte modeldienst. De herhaalde echte proef volgt na de aangescherpte stagingdeploy.
- Na de aanscherping slagen alle 94 offline testmethoden. De totale toevoeging raakt zeven bestanden; llm.py bevat alleen de extra MHJH-broninstructie, de gedeelde YellowMind-route behoudt zijn bestaande instructie.

## Brongebonden antwoord na tweede echte proef
- Render bevestigde 18ae905671b969565192478d12317928434701f3 als Live (1m07s). De tweede proef herkende beide namen, maar directe identiteit en verkorte uitleg lieten de bron opnieuw weg; de uitgebreide uitleg noemde Dennis pas na de onbeperkte claim. Alleen een promptregel bleek dus onvoldoende.
- De DaBuddha-kenniskaart bevat daarom nu één compact brongebonden antwoord met naamvarianten en fotografietrefwoorden. Een lokale antwoordcontrole in de Gabber-route gebruikt uitsluitend zo een volledig aanwezige kaart uit de geselecteerde gecontroleerde kennis. Als de gegenereerde tekst de bijbehorende fotografieclaim gebruikt, wordt het antwoord vervangen door de vastgelegde identiteit plus de zin Volgens Dennis van MHJH. Feiten staan in de kenniskaart, niet dubbel hardgecodeerd in de antwoordcontrole. Chatgeschiedenis of gebruikersinvoer kan geen kaart leveren.
- De controle voegt geen modelaanroep of query toe en behoudt de bestaande tokenregistratie. Zonder kaart of zonder passende namen en fotografietrefwoorden blijft het modelantwoord behouden. YellowMind gebruikt deze controle niet. Dit is een gerichte bescherming voor expliciet gemarkeerde kaarten, geen algemene bewijs- of persoonsvalidator.
- Alle 96 offline unittest-methoden slagen. Twee extra tests dekken de concrete ongeattribueerde antwoorden uit de echte proef, ontbreken van een kaart, gewone identiteit/Bridgeway-antwoorden en de echte modelantwoordgrens met behoud van usage en precies één modelaanroep. De totale wijziging blijft zeven bestanden. Definitieve deploy en herhaalde echte proef volgen.

## Bevestigde toevoeging DaBuddha en Bridgeway op staging
- Definitieve stagingcommit 6cc69be993cb4f95ed34e7bb38c215ebb71eaccc staat op askyellow-staging/main. Render bevestigt Live, duur 1m17s: https://dashboard.render.com/web/srv-d4et0ne3jp1c738nklcg/deploys/dep-dbjkradg1s2s7382lps0.
- Vier echte vragen na deze deploy bevestigen DaBuddha-herkenning, de relatie met Mirko/Thunderdome, bronbehoud bij inkorten en Bridgeway-herkenning. Alle drie fotograafantwoorden geven de gecontroleerde tekst met Volgens Dennis van MHJH, zonder toegevoegd recentelijk of een startjaar. Het Bridgeway-antwoord noemt het platenlabel, de opnamestudio en het dj-platform in Waddinxveen.
- Het brongebonden antwoord blijft bewust twee korte zinnen bij een verzoek om inkorten; de bron wordt behouden. De eerdere eerste proef had de verjaardagsketen, het verschil tussen Bridgeway-liveset en labelrelease en de onbekende fictieve naam al gecontroleerd. De laatste vier vragen richten zich op de daarna gewijzigde bronbehandeling.
- 96 offline tests slagen; de definitieve vergelijking met a1c6824cd029c38baa20e4f4f00dcd82e805cc0b omvat uitsluitend de zeven beschreven bestanden. Geen wijziging aan selectie/scoring, maximaal drie passages of contextbudget. Geen extra model- of databaseoproep.
- Productie/main is gedurende de afronding opnieuw gecontroleerd en staat nog op 36b44b58b1388de48f543a283e948f64efc0231b. Geen productiepromotie uitgevoerd. Ronde 7, de onbekende-persoonreparatie en deze toevoegingen blijven op staging voor Dennis’ praktijktest en afzonderlijke gouden knop.

## Gouden knop ronde 7 en laatste stagingreparaties — 1 november 2026
- Dennis heeft de stagingwerking goed bevonden en expliciet de gouden knop gegeven om de laatste wijzigingen naar main te zetten. Deze toestemming omvat de nog niet gepromoveerde ronde 7, de gerichte bescherming bij onbekende namen, DaBuddha/Bridgeway en de brongebonden fotograafkennis. Geaccepteerde stagingstand: 6cc69be993cb4f95ed34e7bb38c215ebb71eaccc.
- Productie is vooraf opnieuw gelezen: askyellow-ai/main staat op 36b44b58b1388de48f543a283e948f64efc0231b. Dit is het terugvalpunt voor deze release. Staging en productie zijn per tree vergeleken; de lokaal gebruikte stagingbestanden zijn met hun Git-blobs gecontroleerd.
- De productiekandidaat neemt alleen de zes relevante runtimebestanden over: core/mhjh_context.py, core/personalities.py, llm.py en de kennisbestanden voor ronde 2, 5 en 7. Daarnaast drie bijbehorende regressietests en deze blueprint: tien bestanden totaal. De kennisloader en de drie kennisbestanden plus de tests komen rechtstreeks uit de geaccepteerde stagingstand.
- core/personalities.py en llm.py zijn gericht gecombineerd met productie. De goedgekeurde persona-, smaak-, onbekende-naam- en bronregels gaan mee. Een oudere stagingregel over webmogelijkheden en een oudere algemene actualiteitsinstructie gaan niet mee met deze kennisrelease. De overige productiecode, actuele operationele JSON, routes, tijdcontext, affiliatecode en infrastructuur blijven behouden. YellowMind houdt zijn bestaande profiel en route. Geen database- of secretwijziging.
- De volledige set van 96 offline unittest-methoden slaagt met de productiekandidaat en de productieversies van chat.py, lineup.json en tickets.json. Dit omvat de 89 bestaande kennisvraagcontroles, ronde-7-gedrag, de onbekende-persoonketen en de echte modelgrenzen met gemockte diensten. Geen echte model- of databaseoproepen tijdens deze offline tests.
- Publicatie naar productie, Render-deploy en echte productievragen volgen na het vastleggen van deze kandidaat. De gouden knop is ontvangen; deze vermelding claimt nog geen actieve deploy.
