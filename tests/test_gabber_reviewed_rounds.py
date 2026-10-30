"""Offline retrieval checks for the approved 29 October 2026 additions.

No model calls, credentials, external requests or conversation data are used.
Run with: python -m unittest discover -s tests -p test_gabber_reviewed_rounds.py
"""
import unittest

from core.mhjh_context import _hardcore_matches


class ReviewedRoundsRetrievalTests(unittest.TestCase):
    def test_reviewed_additions_are_retrievable(self):
        checks = (
            ("Kan Ruffian ook als dj draaien?", "ook als dj"),
            ("Wie is The Satan?", "Rusland"),
            ("Wat is Peacock in Concert?", "live muzikanten"),
            ("Wie is Omar Santana?", "Amerikaanse"),
            ("Wie is Scott Brown?", "Schotse"),
            ("Wie is Hellfish?", "Britse"),
            ("Hoe ontstond hardcore en blijft het zich ontwikkelen?", "ontwikkelingsproces"),
            ("Wat is het verschil tussen een liveact en een dj set?", "samplers"),
            ("Wie heeft hardcore uitgevonden?", "Niemand alleen"),
        )
        for question, expected in checks:
            with self.subTest(question=question):
                excerpts = _hardcore_matches(question)
                selected = "\n\n".join(excerpts)
                self.assertIn(expected.casefold(), selected.casefold())
                self.assertLessEqual(len(excerpts), 3)
                self.assertLessEqual(len(selected), 7200)
                self.assertNotIn("GEEN OPMERKINGEN", selected)
                self.assertNotIn("Redactionele correctie:", selected)


class ReviewedRoundThreeRetrievalTests(unittest.TestCase):
    def test_reviewed_scene_history_is_retrievable(self):
        checks = (
            ("Waar stond Mysteryland in 1998?", "Lingebos"),
            ("Heeft Mysteryland in 2026 een editie?", "sloeg 2026 over"),
            ("Is Mysteryland een meerdaags festival met camping?", "camping"),
            ("Wanneer is Mysteryland 2027?", "27, 28 en 29 augustus"),
            ("Is Mysteryland gestopt?", "niet definitief gestopt"),
            ("Waar stond Dominator in 2008?", "Vlietland"),
            ("Is Dominator een weekendfestival met camping?", "camping"),
            ("Dominator camping", "bijbehorende weekendticket"),
            ("Wanneer was Ghosttown I?", "11 september 1993"),
            ("Wanneer was de eerste Ghosttown?", "11 september 1993"),
            ("Wat is Ghosttown?", "Dance 2 Eden"),
            ("Wie organiseerde Ghosttown?", "Dance 2 Eden"),
            ("Waar begon Ghosttown?", "Vechtsebanen"),
            ("Zijn Hellbound en Hellraiser hetzelfde?", "verschillende"),
            ("Is Raving Nightmare hetzelfde als A Nightmare in Rotterdam?", "afzonderlijk"),
            ("Wat was Global Hardcore Nation in Antwerpen in 1997?", "honderd"),
            ("Wanneer was Operatie Staartjes?", "15 mei 1993"),
            ("Wat is Operatie Staartjes?", "15 mei 1993"),
            ("Heeft Mirko Kuit publieke fotos gemaakt bij Den Haag Hakkûh II?", "geen publieke"),
            ("Mirko Kuit fotos editie II", "geen publieke"),
            ("Waar was Decibel in 2005?", "Lingebos"),
        )
        for question, expected in checks:
            with self.subTest(question=question):
                excerpts = _hardcore_matches(question)
                selected = "\n\n".join(excerpts)
                self.assertIn(expected.casefold(), selected.casefold())
                self.assertLessEqual(len(excerpts), 3)
                self.assertLessEqual(len(selected), 7200)
                self.assertNotIn("Opmerking in blauw:", selected)
                self.assertNotIn("Actualisatie ter controle", selected)
                self.assertNotIn("Welke rode passage keuren", selected)
                self.assertNotIn("34 verhuisdozen", selected)
                self.assertNotIn("gevelletters", selected)

    def test_mirko_correction_has_no_conflicting_future_promise(self):
        for question in ("Mirko Kuit fotos editie II", "Mirko de Onvindbare", "Zijn mening over Den Haag Hakkûh II"):
            with self.subTest(question=question):
                selected = "\n\n".join(_hardcore_matches(question))
                self.assertIn("geen publieke foto’s", selected)
                self.assertNotIn("haalt voor Den Haag Hakkûh II zijn camera", selected)
                self.assertNotIn("via de MHJH-familie weer bij evenementen fotografeert", selected)


class ReviewedRoundFourRetrievalTests(unittest.TestCase):
    def test_reviewed_clothing_and_culture_answers_are_retrievable(self):
        checks = (
            ("Waar komt Australian vandaan en wanneer begon het merk?", "1956"),
            ("Is de Australian Archive Line uit 2023 een oud origineel?", "hedendaagse"),
            ("Wanneer kwam de Nike Air Max BW uit?", "1991"),
            ("Wat betekent BW bij Nike Air Max?", "Big Window"),
            ("Wie begonnen Exactitudes?", "Ari Versluis"),
            ("Cavello als gabbermerk naast Australian", "Dennis"),
            ("Klassieke gabberlook met Cavello en Air Max", "100% gabber"),
            ("De Air Max BW bij grime en bubbling", "bubbling"),
            ("Thunderdome tattoo toegang procedure", "tattoo-ticket"),
            ("Hakken persoonlijke dansstijl", "choreografie"),
            ("Gabbercultuur overdracht generaties", "familie"),
            ("Oude kleding verzamelen herkomst", "eigenaar"),
        )
        for question, expected in checks:
            with self.subTest(question=question):
                excerpts = _hardcore_matches(question)
                selected = "\n\n".join(excerpts)
                self.assertIn(expected.casefold(), selected.casefold())
                self.assertLessEqual(len(excerpts), 3)
                self.assertLessEqual(len(selected), 7200)
                self.assertNotIn("YES! top!", selected)
                self.assertNotIn("review-feedback", selected)
                self.assertNotIn("Welke nieuwe passage", selected)

    def test_locker_answers_do_not_restore_an_undated_fixed_price(self):
        from core.mhjh_context import get_relevant_mhjh_context
        for question in (
            "Wat kosten lockers bij Whitehouse?",
            "Whitehouse praktische partyinfo lockers",
            "Welke prijs geldt voor een kluis?",
        ):
            with self.subTest(question=question):
                selected = get_relevant_mhjh_context(question) or ""
                self.assertIn("concrete editie", selected)
                self.assertNotIn("€6", selected)
                self.assertNotIn("€ 6", selected)

    def test_runtime_knowledge_excludes_review_and_unbuilt_workshop_promises(self):
        from core.mhjh_context import HARDCORE_DIR
        path = HARDCORE_DIR / "Gabber_Yello_Hardcorekennis_Ronde_4_Kleding_Dansstijl_Gebruiken.md"
        text = path.read_text(encoding="utf-8")
        for unwanted in (
            "concept ter controle", "Controlelijst voor Dennis",
            "Controlepunten voor Dennis en Fer", "review-feedback",
            "YES! top!", "opgeschroren", "hakkenworkshop",
            "Deze aanvulling bevestigt die prijs niet opnieuw",
        ):
            self.assertNotIn(unwanted, text)
        self.assertIn("goedgekeurd door Dennis", text)
        self.assertIn("sceneherkenning van Dennis", text)


class ReviewedRoundFiveRetrievalTests(unittest.TestCase):
    def test_reviewed_release_facts_and_definitions_are_retrievable(self):
        checks = (
            ("Wat is een testpersing?", "geluidskwaliteit"),
            ("Is een white label automatisch een testpersing?", "niet mechanisch"),
            ("Wat betekent promo bij een plaat?", "promotiedoel"),
            ("Identificeert een catalogusnummer iedere persing uniek?", "niet op zichzelf"),
            ("Waar staat het matrixnummer op vinyl?", "uitloopgroef"),
            ("Wat is het verschil tussen reissue en repress?", "oorspronkelijke masterdisc"),
            ("Zijn label en distributeur dezelfde rol?", "verschillende rollen"),
            ("Wie begon Mokum Records bij Boudisque?", "Fred Berkhout"),
            ("Mokum Records en Roadrunner", "1992"),
            ("Name Of The DJ MOK265 versies", "Cyanide Remixxx Remastered"),
            ("Is 14 juli 2022 de eerste persing van Name Of The DJ?", "afzonderlijke controle"),
            ("DJ Chosen Few MOK265 credits", "François Prijt"),
            ("Wie doet The Break op MOK265?", "DJ Pila"),
            ("DJ T-go Let It Roar MOK324", "1 mei 2025"),
            ("DJ T-go Let It Roar Technohead Remix credits", "Tygo Ouwerkerk"),
            ("Wie deed mastering en artwork voor Let It Roar?", "Wicked XXX"),
            ("Call The Man Buzz Fuzz Remix Industrial Strength", "Satronica"),
            ("Extreme Terror Kenny Campbell remix", "DJ Skinhead"),
            ("Kom Tie Dan Hè Top 40 hoeveel weken Digidance", "acht weken"),
            ("Den Haag Hakkûh en De Haag Hakke verschillende platen", "1993"),
            ("Trackherkenning mixidentificatie MHJH-context", "geen persoonlijke plaatherinneringen"),
        )
        for question, expected in checks:
            with self.subTest(question=question):
                excerpts = _hardcore_matches(question)
                selected = "\n\n".join(excerpts)
                self.assertIn(expected.casefold(), selected.casefold())
                self.assertLessEqual(len(excerpts), 3)
                self.assertLessEqual(len(selected), 7200)
                self.assertNotIn("Controlepunten voor Dennis", selected)
                self.assertNotIn("Fer riep gelijk", selected)

    def test_runtime_replaces_conflicts_and_excludes_review(self):
        from core.mhjh_context import HARDCORE_DIR
        path = HARDCORE_DIR / "Gabber_Yello_Hardcorekennis_Ronde_5_Platen_Labels_Bekende_Tracks.md"
        text = path.read_text(encoding="utf-8")
        for unwanted in (
            "concept ter controle", "Testpressing of white label",
            "De unieke code waarmee", "Controlelijst voor Dennis",
            "Controlepunten voor Dennis en Fer", "Voorgestelde",
            "reviewfase", "Voor Dennis was dit de plaat van die avond",
            "Fer riep gelijk", "Yes!!", "welke nieuwe passage",
        ):
            self.assertNotIn(unwanted, text)
        for expected in (
            "goedgekeurd door Dennis", "geen persoonlijke plaatherinneringen",
            "Komt Tie Dan He", "Den Haag Hakkûh",
            "de muziek pas in 2022 ontstond", "https://mokumrecords.bandcamp.com/album/mok265",
        ):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()

