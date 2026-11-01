"""Round 7 selection and real prompt-boundary checks, with no providers or database."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from core.mhjh_context import get_relevant_mhjh_context
from core.personalities import get_personality_profile, YELLOWMIND_PROFILE

ROOT=Path(__file__).resolve().parents[1]

class RoundSevenTests(unittest.TestCase):
 def call_boundary(self, question, kb=None, personality="gabber_yello"):
  source=ast.parse((ROOT/"llm.py").read_text(encoding="utf-8"))
  function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=="call_yello_llm")
  create=Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="offline"))]))
  ns={"os":SimpleNamespace(getenv=lambda key,default=None:default),
      "client":SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))),
      "log_ai_token_usage":Mock(return_value={}),"get_personality_profile":get_personality_profile,
      "YELLO_CORE_PROMPT":"Core","_remove_gabber_auto_followup":lambda s:s}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),"llm.py","exec"),ns)
  ns["call_yello_llm"](question,"nl",kb,None,{},history=[],personality=personality,knowledge_label="MHJH" if personality=="gabber_yello" else "AskYellow")
  self.assertEqual(create.call_count,1)
  return create.call_args.kwargs["messages"]

 def test_approved_behavior_reaches_every_gabber_model_call(self):
  for question in ["Ik hou van uptempo","Vertel iets over hakken","Wie heeft dit gecontroleerd?","Was jij vroeger in de Energiehal?"]:
   with self.subTest(question=question):
    messages=self.call_boundary(question)
    profile=messages[1]["content"]
    for rule in ["met elke hardcore- en harddancestijl", "bijl", "vaste afsluitzin", "herkomst van de specifieke passage", "digitale persona"]:
     self.assertIn(rule,profile)
    self.assertEqual(messages[-1],{"role":"user","content":question})

 def test_yellowmind_uses_its_existing_profile(self):
  messages=self.call_boundary("Hallo",personality="yellowmind")
  self.assertEqual(messages[1]["content"],YELLOWMIND_PROFILE)
  self.assertNotIn("bijl",messages[1]["content"])

 def test_favorite_context_allows_grounded_choice_without_fixed_ranking(self):
  context=get_relevant_mhjh_context("Wat is jouw favoriete track?")
  for alternative in ["Wat vind jij de beste track?", "Wat vind je de beste hardcore track?"]:
   self.assertIn("noem dan GEEN concrete track",get_relevant_mhjh_context(alternative))
  self.assertIn("Je mag op een concreet muzikaal criterium",context)
  self.assertIn("daadwerkelijk met die credits staat",context)
  self.assertNotIn("laat het daarbij",context)
  self.assertNotIn("Noem daarom geen exacte track",context)
  messages=self.call_boundary("Wat is jouw favoriete track?",context)
  self.assertTrue(any(context in m["content"] for m in messages if m["role"]=="system"))

 def test_retrieval_covers_approved_style_humor_sources_and_mirko(self):
  cases=[
   ("Hoe ga je om met early en elke stijl?","brengt niet ieder gesprek terug naar early"),
   ("Gebruik je hakken met een bijl als afsluitzin?","niet als vaste afsluitzin"),
   ("Mag je Dennis en Fer als bron noemen?","herkomst van die specifieke kennis"),
   ("Heeft Mirko bij editie II publieke foto’s gemaakt?","geen publieke"),
   ("Wat is jouw favoriete track?","geen nieuwe vaste favoriete tracks"),
  ]
  for question,marker in cases:
   with self.subTest(question=question):
    self.assertIn(marker,get_relevant_mhjh_context(question) or "")

 def test_runtime_excludes_review_and_unresolved_track_placeholders(self):
  text=next((ROOT/"gabber_yello/knowledge/hardcore").glob("*Ronde_7*")).read_text(encoding="utf-8")
  for removed in ["Controlelijst voor Dennis en Fer","Reviewvragen bij deze ronde","Antwoord Dennis:",
                  "[gecontroleerde artiest en titel]","Nieuw correctievoorstel",
                  "en soms bij Mirko op de camera"]:
   self.assertNotIn(removed,text)
  self.assertIn("geen vastgestelde favorietenlijst",text)
  self.assertIn("aangekondigde set",text)

 def test_named_source_claim_is_conditional_at_model_boundary(self):
  profile=self.call_boundary("Is al jouw kennis door Dennis en Fer gecontroleerd?")[1]["content"]
  self.assertIn("uitsluitend wanneer de aangeleverde kennis de herkomst van de specifieke passage vastlegt",profile)
  self.assertIn("Geef anders geen persoonlijke bronclaim",profile)

 def test_gabber_wrapper_does_not_invent_a_pair_when_retrieval_has_none(self):
  import re
  source=ast.parse((ROOT/"llm.py").read_text(encoding="utf-8"))
  wrapper=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=="call_gabber_yello_llm")
  call=Mock(return_value=("grounded",{}))
  ns={"re":re,"call_yello_llm":call}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[])),"llm.py","exec"),ns)
  for question in ["Wat vind jij de beste track?", "Wat is jouw favoriete track?"]:
   context=get_relevant_mhjh_context(question)
   answer,usage=ns["call_gabber_yello_llm"](question,kb_answer=context)
   self.assertIn("eigen sound",answer)
   self.assertIsNone(usage)
  call.assert_not_called()
  context="PERSONA-SMAAK — KIEZEN OP EEN CRITERIUM\n- *Dominator* — Human Resource;"
  self.assertEqual(ns["call_gabber_yello_llm"]("favoriete track?",kb_answer=context),("grounded",{}))
  call.assert_called_once()

if __name__=="__main__":
 unittest.main()
