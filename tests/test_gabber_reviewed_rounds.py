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


if __name__ == "__main__":
    unittest.main()
