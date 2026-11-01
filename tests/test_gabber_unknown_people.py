"""Unknown names in birthday smalltalk and identity follow-ups; no providers."""
import ast
from pathlib import Path
import re
import unittest
from unittest.mock import Mock
from core.mhjh_context import unverified_person_reply, _unknown_name_note

ROOT=Path(__file__).resolve().parents[1]
FIRST="jaaa vrijdag verjaardag gehad van borrelmaatx, was gezellig en druk"
OLD="Borrelmaatx is een goede naam in de scene, dus ik kan me voorstellen dat het een knal was!"

class UnknownPersonTests(unittest.TestCase):
 def test_unknown_chain_stays_warm_without_scene_claim(self):
  first=unverified_person_reply(FIRST)
  self.assertIn("gezellig",first)
  history=[{"role":"user","content":FIRST},{"role":"assistant","content":first}]
  second=unverified_person_reply("ja? ken je borrelmaatx?",history)
  self.assertIn("Borrelmaatx niet betrouwbaar plaatsen",second)
  for text in [first,second]:
   for forbidden in ["goede naam","knalfeest","bekende artiest","Wat maakt"]:
    self.assertNotIn(forbidden,text)

 def test_stale_assistant_claim_is_retracted_instead_of_reused(self):
  history=[{"role":"user","content":FIRST},{"role":"assistant","content":OLD}]
  reply=unverified_person_reply("ja? ken je borrelmaatx?",history)
  self.assertIn("was niet onderbouwd",reply)
  self.assertIn("niet betrouwbaar plaatsen",reply)
  self.assertNotIn("goede naam",reply)

 def test_lowercase_case_and_multiword_names_get_the_same_guard(self):
  for name in ["borrelmaatx","Borrelmaatx","BORRELMAATX","borrel maatx","borrelmaatx"]:
   with self.subTest(name=name):
    self.assertIn("niet betrouwbaar plaatsen",unverified_person_reply("ken je "+name+"?"))
    self.assertIsNotNone(_unknown_name_note("ken je "+name+"?",""))
    self.assertIn("gezellig",unverified_person_reply("verjaardag gehad van "+name+", was gezellig"))

 def test_known_people_and_ordinary_questions_keep_model_route(self):
  for question in ["ken je Darkraver?","ken je DJ Rob?","ken je Hans Glock?",
                   "ken je mij?","ken je een leuke dj?","Vertel over Mysteryland",
                   "Wat kost een kaartje voor de verjaardag van borrelmaatx?",
                   "Schrijf een felicitatie voor de verjaardag van borrelmaatx"]:
   with self.subTest(question=question):
    self.assertIsNone(unverified_person_reply(question))

 def test_pronoun_uses_recent_user_topic_not_assistant_facts(self):
  history=[{"role":"user","content":FIRST},{"role":"assistant","content":OLD}]
  self.assertIn("Borrelmaatx",unverified_person_reply("ken je hem?",history))
  history+=[{"role":"user","content":"Vertel nu over Mysteryland"},
            {"role":"assistant","content":"Borrelmaatx is een legende."}]
  self.assertIsNone(unverified_person_reply("ken je hem?",history))

 def test_recent_bounded_history_and_denials_do_not_become_reputation(self):
  history=[{"role":"user","content":FIRST},{"role":"assistant","content":"Ik kan Borrelmaatx niet betrouwbaar plaatsen."}]
  self.assertNotIn("was niet onderbouwd",unverified_person_reply("ken je borrelmaatx?",history))
  old=[{"role":"assistant","content":OLD}]+[{"role":"assistant","content":"Hallo"}]*8
  self.assertNotIn("was niet onderbouwd",unverified_person_reply("ken je borrelmaatx?",old))

 def test_birthday_is_not_independent_knowledge(self):
  history=[{"role":"user","content":FIRST}]
  self.assertEqual(unverified_person_reply("wie is borrelmaatx?",history),"Ik kan Borrelmaatx niet betrouwbaar plaatsen.")

 def test_actual_gabber_wrapper_skips_model_for_both_unknown_turns(self):
  tree=ast.parse((ROOT/"llm.py").read_text(encoding="utf-8"))
  wrapper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="call_gabber_yello_llm")
  model=Mock(return_value=("normal",{}))
  ns={"re":re,"call_yello_llm":model}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[])),"llm.py","exec"),ns)
  answer,usage=ns["call_gabber_yello_llm"](FIRST)
  self.assertIn("gezellig",answer);self.assertIsNone(usage)
  history=[{"role":"user","content":FIRST},{"role":"assistant","content":OLD}]
  answer,usage=ns["call_gabber_yello_llm"]("ja? ken je borrelmaatx?",history=history)
  self.assertIn("was niet onderbouwd",answer);self.assertIsNone(usage)
  model.assert_not_called()
  self.assertEqual(ns["call_gabber_yello_llm"]("ken je Darkraver?"),("normal",{}))
  model.assert_called_once()

 def test_distress_questions_and_negative_stories_keep_normal_assistance(self):
  for question in [FIRST+", iemand werd onwel en heeft hulp nodig",
                   "ken je borrelmaatx? hij is bewusteloos, help",
                   "verjaardag gehad van borrelmaatx, was niet gezellig",
                   "verjaardag gehad van borrelmaatx, was vervelend"]:
   with self.subTest(question=question):
    self.assertIsNone(unverified_person_reply(question))

if __name__=="__main__":unittest.main()
