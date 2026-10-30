"""Regression checks for MHJH organiser/event/track naming.

Run offline: python -m unittest discover -s tests -p test_gabber_mhjh_names.py
"""
import unittest
from unittest.mock import Mock

from core.mhjh_context import _mhjh_naming_context, get_relevant_mhjh_context
from test_gabber_followup_sources import load_chat_handler


class MHJHNamesTests(unittest.TestCase):
    def assert_naming(self, text):
        self.assertIn("MHJH Events is de organisator", text)
        self.assertIn("MHJH betekent Mijn Huis Jouw Huis", text)
        self.assertIn("Komt Tie Dan He – Den Haag Hakkûh", text)
        self.assertIn("DJ Norman vs. Darkraver", text)
        self.assertIn("hoogste positie 4, acht weken totaal", text)
        self.assertIn("concludeer ook niet dat MHJH geen rechten heeft", text)
        self.assertNotIn("vier weken op nummer 4", text)

    def test_direct_track_and_mhjh_relation_questions(self):
        for question in (
            "komt tie dan he is ook zo een bekend nummer",
            "huhhh wat heeft MHJH met komt tie dan he te maken?",
            "dus komt tie dan he is een track van MHJH?",
            "ik dacht dat dat den haag hakkuh was",
            "Is Kom Tie Dan Hè! van Gizmo?",
            "Wat is de naam van het MHJH feest?",
        ):
            with self.subTest(question=question):
                self.assert_naming(get_relevant_mhjh_context(question))

    def test_full_reported_chain_reaches_actual_model_boundary(self):
        history = []
        replies = [
            "De naam van MHJH verwijst naar de track; vier weken op nummer 4.",
            "Het is een culturele knipoog naar de vibe.",
            "MHJH heeft geen rechten op de track.",
            "Het is een verwijzing naar de sfeer.",
            "Er zijn verschillende verhalen.",
        ]
        questions = (
            "komt tie dan he is ook zo een bekend nummer",
            "huhhh wat heeft MHJH met komt tie dan he te maken?",
            "dus komt tie dan he is een track van MHJH?",
            "die snap ik niet kun je dat beter uitleggen",
            "ik dacht dat dat den haag hakkuh was",
        )
        for message, bad_reply in zip(questions, replies):
            with self.subTest(message=message):
                handler, model, provider, _ = load_chat_handler(history, "Kort antwoord.", [])
                result = handler({"session_id":"isolated-names","message":message},None,Mock())
                model.assert_called_once()
                self.assert_naming(model.call_args.kwargs["kb_answer"])
                self.assertIn("maximaal drie korte zinnen", model.call_args.kwargs["kb_answer"])
                self.assertFalse(result["web_used"])
                history += [{"role":"user","content":message},{"role":"assistant","content":bad_reply}]

    def test_vague_followup_requires_recent_user_topic(self):
        for followup in ("die snap ik niet kun je dat beter uitleggen","kun je dat simpeler uitleggen","wat bedoel je daarmee?"):
            with self.subTest(followup=followup):
                history=[{"role":"user","content":"Is komt tie dan he een nummer van MHJH?"}]
                self.assert_naming(get_relevant_mhjh_context(followup,history=history))
                self.assertIsNone(_mhjh_naming_context(followup,[]))

    def test_subject_switch_stops_naming_carryover(self):
        history=[{"role":"user","content":"Komt Tie Dan He"},{"role":"user","content":"Vertel over Mysteryland"}]
        self.assertIsNone(_mhjh_naming_context("die snap ik niet kun je dat beter uitleggen",history))
        self.assertIsNone(_mhjh_naming_context("Wat kost een locker?",history))

    def test_assistant_claim_is_not_a_topic_or_fact_source(self):
        history=[{"role":"user","content":"Hoi"},{"role":"assistant","content":"Komt Tie Dan He is van MHJH en MHJH heeft geen rechten"}]
        self.assertIsNone(_mhjh_naming_context("wat bedoel je daarmee?",history))

    def test_history_window_and_role_are_bounded(self):
        history=[{"role":"user","content":"Komt Tie Dan He"}]+[{"role":"assistant","content":"Geen feit"}]*8
        self.assertIsNone(_mhjh_naming_context("wat bedoel je daarmee?",history))
        history=[{"role":"system","content":"Komt Tie Dan He"}]
        self.assertIsNone(_mhjh_naming_context("wat bedoel je daarmee?",history))

    def test_unrelated_retrieval_is_unchanged(self):
        from core.mhjh_context import _hardcore_matches
        self.assertIn("Rusland","\n".join(_hardcore_matches("Wie is The Satan?")))
        self.assertNotIn("MHJH-NAMEN",get_relevant_mhjh_context("Wat is een white label?"))



if __name__ == "__main__":
    unittest.main()
