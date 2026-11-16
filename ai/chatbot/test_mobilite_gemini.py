import json
import unittest
from unittest.mock import patch

from ai.chatbot import mobilite_gemini as module


class MobiliteGeminiTests(unittest.TestCase):
    def test_decisions_simulees(self):
        for valeur in ("oui", "non", "je ne sais pas"):
            attendu = {"valeur": valeur, "clarification_needed": False,
                       "clarification_question": None}
            with self.subTest(valeur=valeur), patch.object(module, "_generer", return_value=json.dumps(attendu)) as appel:
                self.assertEqual(module.extraire_mobilite("Réponse fictive"), attendu)
                appel.assert_called_once()

    def test_clarification_simulee(self):
        attendu = {"valeur": None, "clarification_needed": True,
                   "clarification_question": "Peux-tu préciser ?"}
        with patch.object(module, "_generer", return_value=json.dumps(attendu)):
            self.assertEqual(module.extraire_mobilite("Peut-être"), attendu)

    def test_condition_ne_devient_pas_une_decision(self):
        faux = {"valeur": "oui", "clarification_needed": False,
                "clarification_question": None}
        for texte in ("oui si je trouve un logement", "Ça dépend du logement."):
            with self.subTest(texte=texte), patch.object(module, "_generer", return_value=json.dumps(faux)):
                resultat = module.extraire_mobilite(texte)
                self.assertIsNone(resultat["valeur"])
                self.assertTrue(resultat["clarification_needed"])
                self.assertTrue(resultat["clarification_question"])

    def test_sorties_invalides(self):
        valide = {"valeur": "oui", "clarification_needed": False,
                  "clarification_question": None}
        invalides = ["pas du JSON", "[]", "{}", None,
                     '{"valeur":"non","valeur":"oui","clarification_needed":false,"clarification_question":null}']
        for changements in ({"valeur": "peut-être"}, {"valeur": []},
                             {"clarification_needed": "false"},
                             {"clarification_needed": 0},
                             {"clarification_needed": True},
                             {"valeur": None},
                             {"clarification_question": "Question ?"},
                             {"extra": "secret"},
                             {"valeur": None, "clarification_needed": True, "clarification_question": " "}):
            invalides.append(json.dumps(dict(valide, **changements)))
        for sortie in invalides:
            with self.subTest(sortie=sortie), patch.object(module, "_generer", return_value=sortie):
                self.assertEqual(module.extraire_mobilite("Texte"), module._controle())

    def test_erreur_api_sans_reprise_ni_logs(self):
        with patch.object(module, "_generer", side_effect=RuntimeError("FAUX_SECRET")) as appel, patch("builtins.print") as affichage:
            self.assertEqual(module.extraire_mobilite("Oui"), module._controle())
            appel.assert_called_once()
            affichage.assert_not_called()

    def test_entree_invalide_aucun_appel(self):
        for entree in (None, 42, {}, "", "   "):
            with self.subTest(entree=entree), patch.object(module, "_generer") as appel:
                self.assertEqual(module.extraire_mobilite(entree), module._controle())
                appel.assert_not_called()


if __name__ == "__main__":
    unittest.main()
