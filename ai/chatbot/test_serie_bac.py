import unittest
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
from unittest.mock import patch
from copy import deepcopy
from ai.chatbot.questionnaire import traiter_questionnaire

from ai.chatbot.serie_bac import reconnaitre_sciences_mathematiques


class SerieBacTests(unittest.TestCase):
    def test_terminal_complet_et_correction(self):
        source = Path(__file__).with_name("chatbot.py")
        local = source.with_name("profil_test.json")
        avant = local.read_bytes() if local.exists() else None
        for bac, precision, correction, attendu in [
            ("Sciences mathématiques A", [], [], "sciences_mathematiques_a"),
            ("Sciences mathématiques B", [], [], "sciences_mathematiques_b"),
            ("Sciences mathématiques", ["A"], [], "sciences_mathematiques_a"),
            ("Sciences mathématiques", ["je ne sais pas"], [], None),
            ("Sciences mathématiques", [""], [], None),
            ("Sciences mathématiques", ["A"], ["non", "1", "Sciences mathématiques B"], "sciences_mathematiques_b"),
        ]:
            with self.subTest(bac=bac, correction=correction), tempfile.TemporaryDirectory() as tmp:
                script = Path(tmp) / "chatbot.py"
                script.write_bytes(source.read_bytes())
                valeurs = iter([bac, *precision, "Rabat", "informatique", "jeux", "non", "ingénieur", "Python", "0", "privé", *correction, "oui"])
                with patch.object(sys, "path", [str(source.parent), *sys.path]), patch("builtins.input", side_effect=lambda p: next(valeurs)), contextlib.redirect_stdout(io.StringIO()):
                    terminal = runpy.run_path(str(script), run_name="test_bac")
                    terminal["main"]()
                profil = json.loads(script.with_name("profil_test.json").read_text(encoding="utf-8"))
                self.assertTrue(profil["confirme"])
                self.assertEqual(profil["code_bac"], attendu)
        self.assertEqual(local.read_bytes() if local.exists() else None, avant)

    def test_cycle_adaptateur_et_correction(self):
        for bac, precision, code in [
            ("  Sciences mathématiques A  ", None, "sciences_mathematiques_a"),
            ("Sciences mathématiques B", None, "sciences_mathematiques_b"),
            ("Sciences mathématiques", "B", "sciences_mathematiques_b"),
            ("Sciences mathématiques", "je ne sais pas", None),
            ("Sciences mathématiques", "", None),
            ("je ne sais pas", None, None),
        ]:
            with self.subTest(bac=bac, precision=precision):
                r = traiter_questionnaire(None, "start")
                r = traiter_questionnaire(r["etat"], "answer", {"question_code": "bac", "answer_text": bac})
                if precision is not None:
                    self.assertEqual(r["next_question"]["question_code"], "precision_bac")
                    r = traiter_questionnaire(r["etat"], "answer", {"question_code": "precision_bac", "answer_text": precision})
                for texte in ["Rabat", "informatique", "jeux", "non", "ingénieur", "Python"]:
                    r = traiter_questionnaire(r["etat"], "answer", {"question_code": r["next_question"]["question_code"], "answer_text": texte})
                    self.assertFalse(r["errors"])
                r = traiter_questionnaire(r["etat"], "confirm")
                self.assertTrue(r["profile_confirmed"])
                self.assertEqual(r["profile"]["code_bac"], code)
                self.assertEqual(r["profile"]["bac"], bac)
                r = traiter_questionnaire(r["etat"], "reopen")
                r = traiter_questionnaire(r["etat"], "correct", {"question_code": "bac", "answer_text": "Sciences mathématiques"})
                # Une réponse identique conserve sa précision ; un changement l'efface.
                if bac.strip() != "Sciences mathématiques":
                    self.assertIsNone(r["profile"]["code_bac"])
                    self.assertEqual(r["next_question"]["question_code"], "precision_bac")

    def test_ancien_confirme(self):
        textes = dict(bac="Sciences mathématiques", ville_souhaitee="Rabat", interets="", precision_interets="", mobilite="non", objectif="", competences_declarees="")
        etat = {"status": "completed", "expected_question_code": None,
                "answers": {c: {"question_code": c, "answer_text": t} for c, t in textes.items()}}
        avant = deepcopy(etat)
        r = traiter_questionnaire(etat, "reopen")
        self.assertFalse(r["errors"])
        self.assertEqual(r["next_question"]["question_code"], "precision_bac")
        relu = traiter_questionnaire(etat, "confirm")
        self.assertTrue(relu["profile_confirmed"])
        self.assertIsNone(relu["profile"]["code_bac"])
        self.assertEqual(etat, avant)

    def test_series_explicites(self):
        for texte, code in [("Sciences mathématiques A", "A"),
                            ("  SCIENCES MATHEMATIQUES b  ", "B"),
                            ("Je suis en Sciences mathématiques B.", "B")]:
            with self.subTest(texte=texte):
                resultat = reconnaitre_sciences_mathematiques(texte)
                self.assertEqual(resultat["code"], code)
                self.assertEqual(resultat["original_text"], texte)
                self.assertFalse(resultat["clarification_needed"])
                self.assertIsNone(resultat["clarification_question"])

    def test_serie_non_precisee(self):
        resultat = reconnaitre_sciences_mathematiques("Sciences mathématiques")
        self.assertIsNone(resultat["code"])
        self.assertTrue(resultat["clarification_needed"])
        self.assertIn("A ou B", resultat["clarification_question"])

    def test_inconnue_ou_ambigue(self):
        for texte in ["je ne sais pas", "Sciences mathématiques A ou B",
                      "Peut-être Sciences mathématiques A",
                      "Pas Sciences mathématiques B", "A", "", "Sciences physiques"]:
            with self.subTest(texte=texte):
                resultat = reconnaitre_sciences_mathematiques(texte)
                self.assertIsNone(resultat["code"])
                self.assertEqual(resultat["original_text"], texte)

    def test_type_invalide(self):
        resultat = reconnaitre_sciences_mathematiques(None)
        self.assertIsNone(resultat["code"])
        self.assertTrue(resultat["errors"])


if __name__ == "__main__":
    unittest.main()
