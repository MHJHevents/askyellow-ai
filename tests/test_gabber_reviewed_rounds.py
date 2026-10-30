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


if __name__ == "__main__":
    unittest.main()

