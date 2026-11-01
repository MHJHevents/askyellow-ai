"""Reviewed artist/label additions must reach the existing bounded prompt route."""
import ast
from pathlib import Path
import re
import unittest
from unittest.mock import Mock
from core.mhjh_context import get_relevant_mhjh_context, unverified_person_reply

ROOT = Path(__file__).resolve().parents[1]

class ArtistLabelAdditionTests(unittest.TestCase):
    def test_reviewed_artist_aliases_leave_unknown_fallback_and_retrieve_profile(self):
        for name in ["DaBuddha", "dabuddha", "dabudda", "Da Buddha", "Daniel Gouweleeuw"]:
            with self.subTest(name=name):
                question = "ken je " + name + "?"
                context = get_relevant_mhjh_context(question)
                self.assertIsNone(unverified_person_reply(question))
                self.assertIn("Nederlandse dj en entertainer Daniel Gouweleeuw", context)
                self.assertNotIn("HARD NAAMVANGRAIL", context)
        tree = ast.parse((ROOT / "llm.py").read_text(encoding="utf-8"))
        wrapper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "call_gabber_yello_llm")
        model = Mock(return_value=("normal", {}))
        ns = {"re": re, "call_yello_llm": model}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[])), "llm.py", "exec"), ns)
        self.assertEqual(ns["call_gabber_yello_llm"]("ken je dabudda?", kb_answer=get_relevant_mhjh_context("ken je dabudda?")), ("normal", {}))
        model.assert_called_once()

    def test_photo_succession_keeps_its_actual_source_with_artist_context(self):
        for question in ["Wat heeft DaBuddha met Mirko en Thunderdome te maken?", "Wie is dabudda?"]:
            with self.subTest(question=question):
                context = get_relevant_mhjh_context(question)
                self.assertIn("Volgens Dennis van MHJH", context)
                self.assertIn("overgenomen als officieel fotograaf van Thunderdome", context)
                self.assertIn("openbare dj-profielen zijn geen bron voor die opvolging", context)

    def test_bridgeway_label_and_sets_stay_distinct_in_selected_context(self):
        for question in ["Ken je Bridgeway Records?", "Wat is Bridgeway Records Waddinxveen?", "Is een Bridgeway liveset een labelrelease?"]:
            with self.subTest(question=question):
                context = get_relevant_mhjh_context(question)
                self.assertIn("platenlabel, opnamestudio en dj-platform in Waddinxveen", context)
                self.assertIn("iets anders dan een afzonderlijke trackrelease", context)
                self.assertNotIn("HARD NAAMVANGRAIL", context)

    def test_explicit_source_requirement_reaches_actual_model_prompt(self):
        import test_gabber_round7_persona as persona_tests
        question = "Wat heeft DaBuddha met Mirko en Thunderdome te maken?"
        messages = persona_tests.RoundSevenTests().call_boundary(question, get_relevant_mhjh_context(question))
        knowledge = next(m["content"] for m in messages if "Relevante MHJH-kennis" in m["content"])
        self.assertIn("BRONATTRIBUTIE IS VERPLICHT", knowledge)
        self.assertIn("behoud die bron in dezelfde zin", knowledge)
        self.assertIn("Volgens Dennis van MHJH", knowledge)
        self.assertIn("nooit recentelijk", knowledge)


    def test_source_bound_card_replaces_unattributed_photo_claims_only(self):
        from core.mhjh_context import attributed_knowledge_reply
        context = get_relevant_mhjh_context("Wie is DaBuddha?")
        for question, answer in [
            ("Ken je dabudda?", "Hij is recentelijk de nieuwe officiële fotograaf van Thunderdome geworden."),
            ("Wat heeft DaBuddha met Mirko te maken?", "DaBuddha nam het over van Mirko."),
            ("Kun je DaBuddha korter uitleggen?", "DaBuddha is de fotograaf van Thunderdome."),
        ]:
            with self.subTest(question=question):
                result = attributed_knowledge_reply(question, answer, context)
                self.assertIn("Volgens Dennis van MHJH", result)
                self.assertIn("overgenomen als officieel fotograaf van Thunderdome", result)
                self.assertNotIn("recentelijk", result)
                self.assertNotIn("nu de nieuwe", result)
        for question, answer, selected in [
            ("Wie is DaBuddha?", "DaBuddha is een dj.", context),
            ("Ken je Bridgeway Records?", "Bridgeway is een platenlabel.", context),
            ("Wie is DaBuddha?", "Hij is fotograaf van Thunderdome.", None),
        ]:
            self.assertEqual(attributed_knowledge_reply(question, answer, selected), answer)

    def test_actual_answer_boundary_preserves_source_without_extra_model_call(self):
        from types import SimpleNamespace
        from core.personalities import get_personality_profile
        source = ast.parse((ROOT / "llm.py").read_text(encoding="utf-8"))
        function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == "call_yello_llm")
        question = "Ken je dabudda?"
        raw = "Hij is recentelijk de nieuwe fotograaf van Thunderdome geworden."
        for personality in ["gabber_yello", "yellowmind"]:
            create = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=raw))]))
            ns = {
                "os": SimpleNamespace(getenv=lambda key, default=None: default),
                "client": SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))),
                "log_ai_token_usage": Mock(return_value={"tokens": 12}),
                "get_personality_profile": get_personality_profile,
                "YELLO_CORE_PROMPT": "Core",
                "_remove_gabber_auto_followup": lambda s: s,
            }
            exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), "llm.py", "exec"), ns)
            answer, usage = ns["call_yello_llm"](question, "nl", get_relevant_mhjh_context(question), None, {}, personality=personality, knowledge_label="MHJH" if personality == "gabber_yello" else "AskYellow")
            self.assertEqual(usage, {"tokens": 12})
            create.assert_called_once()
            if personality == "gabber_yello":
                self.assertIn("Volgens Dennis van MHJH", answer)
                self.assertNotIn("recentelijk", answer)
            else:
                self.assertEqual(answer, raw)

if __name__ == "__main__":
    unittest.main()
