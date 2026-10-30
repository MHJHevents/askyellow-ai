"""Offline regression checks: no API keys, model calls, network or database writes."""

import ast
from datetime import date
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from gabber_context import resolve_gabber_context, reviewed_edition_pause_reply, subjects_in
from core.mhjh_context import get_relevant_mhjh_context

# Import only the web-routing module, not the provider's unrelated app imports.
with patch.dict(sys.modules, {"websearch": types.SimpleNamespace(do_websearch=Mock())}):
    web = importlib.import_module("gabber_web")

TODAY = date(2026, 10, 29)
HISTORY = [
    {"role": "user", "content": "Vertel me iets over Mysteryland."},
    {"role": "assistant", "content": "Mysteryland is een jaarlijks festival, ook in 2026."},
]
JUNK = [
    {"title": "Floor Jansen & Douwe Bob - Is dit nu later", "snippet": "Eng subtitles", "url": "https://www.youtube.com/watch?v=VzfAMJjq7AM"},
    {"title": "Radio Project ONE: operator Iris Van Styvoort", "snippet": "Radio interview", "url": "https://www.youtube.com/watch?v=fqRnMcaY-qI"},
    {"title": "I'm confused over Nog and Nog steed", "snippet": "r/learndutch", "url": "https://www.reddit.com/r/learndutch/comments/10a9xzc/"},
    {"title": "Ik geniet nog steeds na", "snippet": "Een fantastisch benefietconcert", "url": "https://www.facebook.com/example/videos/4436377759933589/"},
]
PAUSE = {"title": "Mysteryland slaat 2026 over", "snippet": "Mysteryland neemt in 2026 een pauze en keert in 2027 terug.", "url": "https://example.org/mysteryland-pauze"}
RETURN = {"title": "Mysteryland 2027 FAQ", "snippet": "27, 28 en 29 augustus 2027 in Haarlemmermeer, met camping.", "url": "https://www.mysteryland.nl/info"}


class SubjectResolutionTests(unittest.TestCase):
    def test_periods_years_and_genres_are_not_competing_named_subjects(self):
        for text, expected in (
            ("Mysteryland in de jaren negentig", ("Mysteryland",)),
            ("Mysteryland in 1991", ("Mysteryland",)),
            ("Dominator en Frenchcore", ("Dominator",)),
            ("The Satan maakt hardcore en drum-and-bass", ("The Satan",)),
        ):
            with self.subTest(text=text):
                self.assertEqual(subjects_in(text), expected)

    def resolve(self, question, history=HISTORY):
        return resolve_gabber_context(question, history, TODAY)

    def test_exact_reported_followup_keeps_the_topic(self):
        c = self.resolve("jo dus het is er nog steeds?")
        self.assertEqual(c.subjects, ("Mysteryland",))
        self.assertIn("Mysteryland", c.query)
        self.assertIn("2026", c.query)
        self.assertFalse(c.needs_clarification)

    def test_relative_year_is_concrete_before_retrieval(self):
        c = self.resolve("dus dit jaar ook?")
        self.assertIn("2026", c.query)
        self.assertNotIn("dit jaar", c.query)
        self.assertIn("sloeg 2026 over", get_relevant_mhjh_context(c.query))

    def test_challenge_reloads_facts_not_the_previous_wrong_answer(self):
        c = self.resolve("huhhh editie 2026? weet je dat zeker?")
        self.assertEqual(c.subjects, ("Mysteryland",))
        self.assertIn("sloeg 2026 over", get_relevant_mhjh_context(c.query))
        self.assertNotIn("jaarlijks festival, ook in 2026", c.query)

    def test_last_named_user_topic_wins_over_old_topic(self):
        h = HISTORY + [{"role": "user", "content": "Vertel nu over Dominator."}, {"role": "assistant", "content": "Dominator heeft een camping."}]
        c = self.resolve("En de camping?", h)
        self.assertEqual(c.subjects, ("Dominator",))
        self.assertNotIn("Mysteryland", c.query)

    def test_current_named_topic_overrides_history(self):
        self.assertEqual(self.resolve("Bestaat Dominator nog?").subjects, ("Dominator",))

    def test_multiple_subjects_require_one_targeted_question(self):
        h = [{"role": "user", "content": "Vergelijk Mysteryland en Dominator."}]
        c = self.resolve("dus dit jaar ook?", h)
        self.assertTrue(c.needs_clarification)
        self.assertIn("Mysteryland of Dominator", c.clarification)

    def test_missing_subject_does_not_make_a_generic_search(self):
        c = self.resolve("jo dus het is er nog steeds?", [])
        self.assertTrue(c.needs_clarification)
        self.assertEqual(web.build_gabber_web_query("jo dus het is er nog steeds?", [], TODAY), ("", False))

    def test_unknown_person_does_not_inherit_mysteryland(self):
        c = self.resolve("Wie is Dof?")
        self.assertFalse(c.followup)
        self.assertNotIn("Mysteryland", c.query)
        self.assertFalse(web.should_search_web(c.query, False))

    def test_unknown_new_user_subject_blocks_old_assistant_topic(self):
        h = HISTORY + [{"role": "user", "content": "Wie is Dof?"}, {"role": "assistant", "content": "Mysteryland is groot."}]
        self.assertTrue(self.resolve("En bestaat die nog?", h).needs_clarification)

    def test_assistant_topic_can_only_supply_a_reviewed_name(self):
        h = [{"role": "user", "content": "Noem een bekend festival."}, {"role": "assistant", "content": "Mysteryland vond in 2026 plaats."}]
        c = self.resolve("dit jaar ook?", h)
        self.assertEqual(c.subjects, ("Mysteryland",))
        self.assertNotIn("vond in 2026 plaats", c.query)

    def test_source_footer_does_not_change_subject(self):
        h = [{"role": "assistant", "content": "Mysteryland is een festival.\nBronnen: Dominator en Thunderdome"}]
        self.assertEqual(self.resolve("Is het er nog steeds?", h).subjects, ("Mysteryland",))

    def test_artist_followup_is_not_hardcoded_to_festivals(self):
        h = [{"role": "user", "content": "Wie is The Satan?"}]
        self.assertEqual(self.resolve("En waar komt hij vandaan?", h).subjects, ("The Satan",))

    def test_weather_question_is_a_new_topic(self):
        self.assertFalse(self.resolve("Hoe is het weer?").followup)

    def test_time_anchor_does_not_cross_a_subject_switch(self):
        h = [{"role": "user", "content": "Mysteryland in 2026"}, {"role": "user", "content": "Vertel over Dominator"}]
        self.assertIsNone(self.resolve("Weet je dat zeker?", h).year)

    def test_history_is_bounded(self):
        h = HISTORY + [{"role": "user", "content": "lekker kletsen"}] * 14
        self.assertTrue(self.resolve("Is het er nog steeds?", h).needs_clarification)

    def test_relative_year_rollover(self):
        c = resolve_gabber_context("dus dit jaar ook?", HISTORY, date(2027, 1, 1))
        self.assertEqual(c.year, 2027)
        self.assertNotIn("2026", c.query)

    def test_query_budget_does_not_grow_with_history(self):
        c = self.resolve("jo dus het is er nog steeds?", HISTORY * 1000)
        self.assertLessEqual(len(c.query), 300)


class WebRelevanceTests(unittest.TestCase):
    def test_all_four_reported_unrelated_sources_are_rejected(self):
        c = resolve_gabber_context("jo dus het is er nog steeds?", HISTORY, TODAY)
        self.assertEqual(web.filter_gabber_web_results(JUNK, c.query, c.subjects), [])

    def test_unknown_unanchored_query_cannot_validate_sources(self):
        self.assertEqual(web.filter_gabber_web_results(JUNK, "jo dus het is er nog steeds?"), [])

    def test_valid_source_after_four_bad_results_is_kept(self):
        r = web.filter_gabber_web_results(JUNK + [PAUSE, RETURN], "Mysteryland actuele status 2026", ("Mysteryland",))
        self.assertEqual(r, [PAUSE, RETURN])

    def test_named_topic_without_requested_year_is_not_year_evidence(self):
        r = web.filter_gabber_web_results([RETURN], "Mysteryland dus 2026 ook?", ("Mysteryland",))
        self.assertEqual(r, [])

    def test_old_edition_is_not_evidence_for_current_status(self):
        old = {"title": "Mysteryland 2019", "snippet": "Festival met camping", "url": "https://example.org/2019"}
        self.assertEqual(web.filter_gabber_web_results([old], "Mysteryland actuele status 2026", ("Mysteryland",)), [])

    def test_camping_question_requires_camping_evidence(self):
        self.assertEqual(web.filter_gabber_web_results([PAUSE], "Mysteryland camping 2026", ("Mysteryland",)), [])

    def test_topic_in_url_alone_is_not_evidence(self):
        item = {"title": "Learn Dutch", "snippet": "Nog steeds means still", "url": "https://example.org/Mysteryland-2026"}
        self.assertEqual(web.filter_gabber_web_results([item], "Mysteryland 2026", ("Mysteryland",)), [])

    def test_valid_youtube_source_is_not_blanket_blocked(self):
        item = {"title": "The Satan interview", "snippet": "The Satan discusses his music", "url": "https://www.youtube.com/watch?v=valid"}
        self.assertEqual(web.filter_gabber_web_results([item], "The Satan interview", ("The Satan",)), [item])

    def test_explicit_unknown_topic_requires_query_overlap(self):
        self.assertEqual(web.filter_gabber_web_results(JUNK, "Zoek online naar DJ Unieknaam"), [])

    def test_urls_and_duplicates_are_validated(self):
        bad = [dict(PAUSE, url="javascript:alert(1)"), dict(PAUSE, url="https://secret@example.org/a")]
        self.assertEqual(web.filter_gabber_web_results(bad + [PAUSE, PAUSE], "Mysteryland 2026", ("Mysteryland",)), [PAUSE])

    def test_result_budget_is_four(self):
        results = [dict(PAUSE, url=f"https://example.org/{i}") for i in range(10)]
        self.assertEqual(len(web.filter_gabber_web_results(results, "Mysteryland 2026", ("Mysteryland",))), 4)

    def test_opinion_does_not_trigger_a_current_search(self):
        self.assertFalse(web.should_search_web("Vind jij Mysteryland tegenwoordig leuk?", True))

    def test_current_relative_followup_does_trigger_search(self):
        self.assertTrue(web.should_search_web("dus dit jaar ook?", True))

    def test_search_provider_is_not_called_for_unresolved_topic(self):
        with patch.object(web, "do_websearch") as provider:
            query, _ = web.build_gabber_web_query("is het er nog steeds?", [], TODAY)
            self.assertEqual(web.search_web_for_gabber(query), [])
            provider.assert_not_called()


class CitationTests(unittest.TestCase):
    def test_only_used_source_is_published_and_renumbered(self):
        text, sources = web.select_gabber_citations("De camping staat aangekondigd [2].", [PAUSE, RETURN])
        self.assertEqual(sources, [RETURN])
        self.assertEqual(text, "De camping staat aangekondigd [1].")

    def test_grouped_citations_are_renumbered(self):
        text, sources = web.select_gabber_citations("Terugkeer [2, 1].", [PAUSE, RETURN])
        self.assertEqual(text, "Terugkeer [1, 2].")
        self.assertEqual(sources, [RETURN, PAUSE])

    def test_no_citation_does_not_get_a_decorative_source_list(self):
        text, sources = web.select_gabber_citations("Ja, het was er gewoon.", [PAUSE])
        self.assertEqual(sources, [])
        self.assertIn("niet betrouwbaar bevestigen", text)

    def test_invalid_citation_is_not_published(self):
        text, sources = web.select_gabber_citations("Het was er [9].", [PAUSE])
        self.assertEqual(sources, [])
        self.assertNotIn("[9]", text)

    def test_no_results_cannot_have_numbered_web_citations(self):
        text, sources = web.select_gabber_citations("Niet bevestigd [1].", [])
        self.assertEqual((text, sources), ("Niet bevestigd .", []))

    def test_model_generated_footer_is_removed(self):
        text, sources = web.select_gabber_citations("Geen editie [1].\nBronnen: https://invented.invalid", [PAUSE])
        self.assertEqual(text, "Geen editie [1].")
        self.assertEqual(sources, [PAUSE])

    def test_invented_inline_url_is_rejected(self):
        text, sources = web.select_gabber_citations("Ja [1], kijk https://invented.invalid", [PAUSE])
        self.assertEqual(sources, [])


def load_chat_handler(history, answer="Geen Mysteryland-editie in 2026 [1].", results=None):
    """Exercise the actual handler body without importing unrelated app services."""
    source = (Path(__file__).parents[1] / "chat.py").read_text()
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "gabber_yello_chat")
    node.decorator_list = []
    for arg in node.args.args:
        arg.annotation = None
    node.returns = None
    connection = types.SimpleNamespace(close=Mock())
    model = Mock(return_value=(answer, {}))
    provider = Mock(return_value=results if results is not None else JUNK + [PAUSE])
    namespace = {
        "_verified_mhjh_member": lambda request, payload: None,
        "_gabber_conversation_session": lambda member, session: "test:" + session,
        "get_conn": lambda: connection,
        "get_history_for_llm": lambda conn, session: history,
        "_needs_time_context": lambda text: "dit jaar" in text,
        "build_time_context": lambda: "Huidige datum 29 oktober 2026",
        "build_llm_time_hint": lambda: "Avond",
        "_is_forget_all_request": lambda message: False,
        "_is_memory_question": lambda message: False,
        "_is_identity_question": lambda message: False,
        "resolve_gabber_context": lambda q, h: resolve_gabber_context(q, h, TODAY),
        "reviewed_edition_pause_reply": reviewed_edition_pause_reply,
        "UNCONFIRMED_WEB_REPLY": web.UNCONFIRMED_WEB_REPLY,
        "build_gabber_web_query": lambda q, h, resolved=None: web.build_gabber_web_query(q, h, TODAY, resolved),
        "get_relevant_mhjh_context": get_relevant_mhjh_context,
        "should_search_web": web.should_search_web,
        "search_web_for_gabber": provider,
        "filter_gabber_web_results": web.filter_gabber_web_results,
        "filter_gabber_event_results": web.filter_gabber_event_results,
        "find_mhjh_lineup_overlap": lambda results: [],
        "format_web_context": web.format_web_context,
        "select_gabber_citations": web.select_gabber_citations,
        "store_message_pair": Mock(),
        "call_gabber_yello_llm": model,
    }
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, "chat.py", "exec"), namespace)
    return namespace["gabber_yello_chat"], model, provider, namespace


class HandlerRegressionTests(unittest.TestCase):
    def test_realistic_nineties_intro_does_not_create_false_ambiguity(self):
        h = [{"role": "user", "content": "Vertel me over Mysteryland in de jaren negentig."}]
        handler, model, provider, _ = load_chat_handler(h)
        r = handler({"session_id": "isolated", "message": "dus dit jaar ook?"}, None, Mock())
        model.assert_called_once()
        self.assertIn("sloeg 2026 over", model.call_args.kwargs["kb_answer"])
        self.assertNotIn("Bedoel je", r["reply"])

    def test_two_named_festivals_remain_ambiguous_even_for_weekend_followup(self):
        h = [{"role": "user", "content": "Mysteryland festival en Dominator festival dit weekend?"}]
        handler, model, provider, _ = load_chat_handler(h)
        r = handler({"session_id": "isolated", "message": "En de line-up?"}, None, Mock())
        model.assert_not_called()
        provider.assert_not_called()
        self.assertIn("of", r["reply"])

    def test_named_event_rejects_another_event_even_on_the_right_date(self):
        wrong = {"title": "Dominator festival 31 oktober 2026", "snippet": "Hardcore festival", "url": "https://example.org/wrong"}
        handler, model, provider, _ = load_chat_handler([], "Geen passende editie bevestigd.", [wrong])
        r = handler({"session_id": "isolated", "message": "Is Mysteryland festival dit weekend?"}, None, Mock())
        self.assertFalse(r["web_used"])
        self.assertEqual(r["sources"], [])

    def test_full_reported_chain_retrieves_pause_at_every_followup(self):
        history = list(HISTORY)
        for message in ("jo dus het is er nog steeds?", "dus dit jaar ook?", "huhhh editie 2026? weet je dat zeker?"):
            with self.subTest(message=message):
                handler, model, provider, _ = load_chat_handler(history)
                result = handler({"session_id": "isolated", "message": message}, None, Mock())
                args = model.call_args.kwargs
                self.assertIn("sloeg 2026 over", args["kb_answer"])
                self.assertIn("Mysteryland", provider.call_args.args[0])
                self.assertIn("2026", provider.call_args.args[0])
                self.assertIn("Mysteryland", args["hints"]["topic_context"])
                self.assertNotIn("Floor Jansen", args["hints"]["web_context"])
                self.assertEqual(result["sources"], [{"title": PAUSE["title"], "url": PAUSE["url"]}])
                history += [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]

    def test_unresolved_followup_never_calls_model_or_provider(self):
        handler, model, provider, _ = load_chat_handler([])
        result = handler({"session_id": "isolated", "message": "dus dit jaar ook?"}, None, Mock())
        model.assert_not_called()
        provider.assert_not_called()
        self.assertEqual(result["sources"], [])
        self.assertIn("doel je", result["reply"])

    def test_only_irrelevant_results_are_not_sent_as_web_evidence(self):
        handler, model, provider, _ = load_chat_handler(HISTORY, "Volgens gecontroleerde kennis geen editie in 2026.", JUNK)
        result = handler({"session_id": "isolated", "message": "dus dit jaar ook?"}, None, Mock())
        self.assertFalse(model.call_args.kwargs["hints"]["web_search_succeeded"])
        self.assertNotIn("youtube", model.call_args.kwargs["hints"]["web_context"])
        self.assertFalse(result["web_used"])
        self.assertEqual(result["sources"], [])

    def test_provider_failure_does_not_lose_reviewed_knowledge(self):
        handler, model, provider, _ = load_chat_handler(HISTORY, "Volgens gecontroleerde kennis sloeg Mysteryland 2026 over.")
        provider.side_effect = RuntimeError("offline")
        result = handler({"session_id": "isolated", "message": "dus dit jaar ook?"}, None, Mock())
        self.assertIn("sloeg 2026 over", model.call_args.kwargs["kb_answer"])
        self.assertFalse(result["web_used"])

    def test_uncited_results_are_not_published(self):
        handler, model, provider, _ = load_chat_handler(HISTORY, "Ja, het ging gewoon door.")
        result = handler({"session_id": "isolated", "message": "dus dit jaar ook?"}, None, Mock())
        self.assertEqual(result["sources"], [])
        self.assertIn("Mysteryland sloeg 2026 over", result["reply"])
        self.assertNotIn("het ging gewoon door", result["reply"])

    def test_uncited_reply_cannot_invent_a_positive_edition_from_knowledge(self):
        c = resolve_gabber_context("dus dit jaar ook?", [{"role": "user", "content": "Vertel over Dominator"}], TODAY)
        self.assertIsNone(reviewed_edition_pause_reply(c, "### Dominator\nHet festival heeft een camping."))

    def test_dated_fallback_uses_only_the_named_subject_and_year(self):
        c = resolve_gabber_context("dus dit jaar ook?", HISTORY, TODAY)
        wrong = "### Dominator\nDominator sloeg 2026 over."
        self.assertIsNone(reviewed_edition_pause_reply(c, wrong))
        self.assertIsNone(reviewed_edition_pause_reply(c, "### Mysteryland\nMysteryland sloeg 2025 over."))

    def test_chat_assertion_is_not_a_fallback_knowledge_source(self):
        c = resolve_gabber_context("dus dit jaar ook?", HISTORY, TODAY)
        self.assertIsNone(reviewed_edition_pause_reply(c, None))


class ExistingAgendaRoutingTests(unittest.TestCase):
    def test_named_festival_is_not_replaced_by_generic_party_search(self):
        query, event = web.build_gabber_web_query("Is Mysteryland festival dit weekend?", [], TODAY)
        self.assertTrue(event)
        self.assertIn("Mysteryland", query)
        self.assertIn("31 october 2026", query)

    def test_named_weekend_followup_keeps_the_festival(self):
        query, event = web.build_gabber_web_query("En volgend weekend?", HISTORY, TODAY)
        self.assertTrue(event)
        self.assertIn("Mysteryland", query)
        self.assertIn("7 november 2026", query)

    def test_tomorrow_has_a_concrete_date_before_source_filtering(self):
        query, event = web.build_gabber_web_query("Welke hardcore feesten zijn er morgen in Den Haag?", [], TODAY)
        self.assertTrue(event)
        self.assertIn("30 october 2026", query)

    def test_city_and_weekend_anchor_is_preserved(self):
        query, event = web.build_gabber_web_query("Welke hardcore feesten zijn er dit weekend in Den Haag?", [], TODAY)
        self.assertTrue(event)
        self.assertIn("Den Haag", query)
        self.assertIn("31 october 2026", query)

    def test_city_correction_after_event_query_stays_supported(self):
        h = [{"role": "user", "content": "Welke hardcore feesten zijn er dit weekend in Den Haag?"}]
        query, event = web.build_gabber_web_query("Nee, in Rotterdam", h, TODAY)
        self.assertTrue(event)
        self.assertIn("Rotterdam", query)
        self.assertTrue(query.startswith("hardcore party Rotterdam"))

    def test_event_source_must_still_match_city_and_date(self):
        query = "hardcore party Den Haag 31 october 2026"
        good = {"title": "Hardcore Den Haag 31 oktober 2026", "snippet": "Line-up", "url": "https://example.org/party"}
        wrong = dict(good, title="Hardcore Amsterdam 31 oktober 2026")
        self.assertEqual(web.filter_gabber_event_results([good, wrong], query), [good])


class ModelPromptTests(unittest.TestCase):
    def test_subject_instruction_reaches_model_without_an_extra_model_call(self):
        source = (Path(__file__).parents[1] / "llm.py").read_text()
        node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "call_yello_llm")
        response = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="Geen editie in 2026."))])
        create = Mock(return_value=response)
        namespace = {
            "YELLO_CORE_PROMPT": "Core",
            "get_personality_profile": lambda name: name,
            "client": types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create))),
            "os": types.SimpleNamespace(getenv=lambda name, default: default),
            "log_ai_token_usage": Mock(return_value={}),
            "_remove_gabber_auto_followup": lambda answer: answer,
        }
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "llm.py", "exec"), namespace)
        namespace["call_yello_llm"](
            question="dus dit jaar ook?", language="nl", kb_answer="Mysteryland sloeg 2026 over.",
            sql_match=None, hints={"topic_context": "Onderwerp Mysteryland; tijdlaag 2026."},
            personality="gabber_yello", knowledge_label="MHJH", history=HISTORY,
        )
        create.assert_called_once()
        self.assertIn({"role": "system", "content": "Onderwerp Mysteryland; tijdlaag 2026."}, create.call_args.kwargs["messages"])
        self.assertEqual(create.call_args.kwargs["temperature"], 0.35)


if __name__ == "__main__":
    unittest.main()
