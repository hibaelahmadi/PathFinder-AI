import contextlib
import io
import json
import unittest
from unittest.mock import patch

from ai.chatbot import interets_gemini as module


class InteretsGeminiTests(unittest.TestCase):
    def setUp(self):
        self.codes = ["categorie_fictive_a", "categorie_fictive_b"]

    def test_interet_clair_et_texte_original(self):
        texte = "  J'aime programmer des petits jeux.  "
        sortie = {"codes": [self.codes[0]], "clarification_needed": False,
                  "clarification_question": None}
        with patch.object(module, "_generer", return_value=json.dumps(sortie)) as appel:
            resultat = module.extraire_interets(texte, self.codes)
        self.assertEqual(resultat, dict(sortie, original_text=texte, errors=[]))
        appel.assert_called_once_with(texte, self.codes)
        self.assertEqual(self.codes, ["categorie_fictive_a", "categorie_fictive_b"])
        resultat["codes"].append("autre_code_fictif")
        self.assertEqual(len(self.codes), 2)

    def test_reponse_vague(self):
        sortie = {"codes": [], "clarification_needed": True,
                  "clarification_question": "Quelle activité t'intéresse le plus ?"}
        with patch.object(module, "_generer", return_value=json.dumps(sortie)):
            resultat = module.extraire_interets("J'aime un peu tout", self.codes)
        self.assertEqual(resultat["codes"], [])
        self.assertTrue(resultat["clarification_needed"])
        self.assertEqual(resultat["clarification_question"], sortie["clarification_question"])
        self.assertEqual(resultat["errors"], [])

    def test_code_invente_rejette_toute_extraction(self):
        sortie = {"codes": [self.codes[0], "code_invente_fictif"],
                  "clarification_needed": False, "clarification_question": None}
        with patch.object(module, "_generer", return_value=json.dumps(sortie)):
            resultat = module.extraire_interets("Texte original", self.codes)
        self.assertEqual(resultat["original_text"], "Texte original")
        self.assertEqual(resultat["codes"], [])
        self.assertTrue(resultat["errors"])
        self.assertTrue(resultat["clarification_needed"])

    def test_indisponibilite_sans_reprise_ni_secret(self):
        sortie = io.StringIO()
        with patch.object(module, "_generer", side_effect=RuntimeError("FAUX_SECRET")) as appel, contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            resultat = module.extraire_interets("Texte préservé", self.codes)
        appel.assert_called_once()
        self.assertEqual(sortie.getvalue(), "")
        self.assertNotIn("FAUX_SECRET", str(resultat))
        self.assertEqual(resultat["original_text"], "Texte préservé")
        self.assertEqual(resultat["codes"], [])
        self.assertTrue(resultat["errors"])

    def test_sorties_invalides(self):
        base = {"codes": [self.codes[0]], "clarification_needed": False,
                "clarification_question": None}
        sorties = ["pas JSON", "[]", "{}", None,
                   '{"codes":[],"codes":[],"clarification_needed":true,"clarification_question":"Précise ?"}']
        for changements in ({"codes": self.codes * 2}, {"codes": [42]},
                             {"codes": []}, {"codes": "texte"},
                             {"clarification_needed": "false"},
                             {"clarification_needed": True},
                             {"extra": True}, {"clarification_question": "Question ?"},
                             {"codes": [], "clarification_needed": True, "clarification_question": " "}):
            sorties.append(json.dumps(dict(base, **changements)))
        for sortie in sorties:
            with self.subTest(sortie=sortie), patch.object(module, "_generer", return_value=sortie):
                resultat = module.extraire_interets("Original", self.codes)
                self.assertEqual(resultat["codes"], [])
                self.assertEqual(resultat["original_text"], "Original")
                self.assertTrue(resultat["errors"])

    def test_entrees_invalides_sans_appel(self):
        for texte, codes in ((None, self.codes), (42, self.codes),
                             ("texte", []), ("texte", None), ("texte", [""]),
                             ("texte", [42]), ("texte", self.codes * 2)):
            with self.subTest(texte=texte, codes=codes), patch.object(module, "_generer") as appel:
                self.assertTrue(module.extraire_interets(texte, codes)["errors"])
                appel.assert_not_called()

    def test_vide_demande_precision_sans_appel(self):
        with patch.object(module, "_generer") as appel:
            resultat = module.extraire_interets("   ", self.codes)
        appel.assert_not_called()
        self.assertEqual(resultat["original_text"], "   ")
        self.assertTrue(resultat["clarification_needed"])
        self.assertEqual(resultat["errors"], [])


if __name__ == "__main__":
    unittest.main()
