import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class MobiliteTerminalTests(unittest.TestCase):
    def parcours(self, mobilite, corrections=(), extraction=None, erreur=None):
        source = Path(__file__).with_name("chatbot.py")
        profil_local = source.with_name("profil_test.json")
        avant = profil_local.read_bytes() if profil_local.exists() else None
        module = types.ModuleType("mobilite_gemini")
        module.extraire_mobilite = Mock(return_value=extraction, side_effect=erreur)
        valeurs = iter(["Sciences", "Rabat", "informatique", "programmation",
                        *mobilite, "ingénierie", "", *corrections, "oui"])
        prompts = []
        sortie = io.StringIO()
        with tempfile.TemporaryDirectory(prefix="pathfinder-terminal-") as tmp:
            script = Path(tmp) / "chatbot.py"
            script.write_bytes(source.read_bytes())
            cible = script.with_name("profil_test.json")

            def repondre(prompt):
                self.assertFalse(cible.exists(), "Sauvegarde avant confirmation finale")
                prompts.append(prompt)
                return next(valeurs)

            with patch.dict(sys.modules, {"mobilite_gemini": module}), \
                    patch.object(sys, "path", [str(source.parent), *sys.path]), \
                    patch("builtins.input", side_effect=repondre), \
                    contextlib.redirect_stdout(sortie):
                etat = runpy.run_path(str(script), run_name="__main__")
            self.assertIsNone(next(valeurs, None), "Réponses de test non consommées")
            profil = json.loads(cible.read_text(encoding="utf-8"))
            self.assertTrue(profil["confirme"])
        self.assertEqual(profil_local.read_bytes() if profil_local.exists() else None, avant)
        return profil, etat, prompts, sortie.getvalue(), module.extraire_mobilite

    def test_interpretation_confirmee(self):
        profil, _, prompts, _, appel = self.parcours(
            ["Je veux rester ici", "oui"],
            extraction={"valeur": "non", "clarification_needed": False,
                        "clarification_question": None},
        )
        self.assertEqual(profil["mobilite"], "non")
        appel.assert_called_once_with("Je veux rester ici")
        self.assertEqual(sum("J’ai compris : non. Est-ce correct ?" in p for p in prompts), 1)
        self.assertEqual(sum("Ce résumé est-il correct" in p for p in prompts), 1)

    def test_interpretation_refusee(self):
        profil, _, _, _, appel = self.parcours(
            ["Je pourrais partir", "non", "non"],
            extraction={"valeur": "oui", "clarification_needed": False,
                        "clarification_question": None},
        )
        self.assertEqual(profil["mobilite"], "non")
        self.assertIsNone(profil["autres_villes"])
        appel.assert_called_once()

    def test_ambiguite_sans_decision(self):
        profil, _, prompts, sortie, appel = self.parcours(
            ["Ça dépend du logement", "je ne sais pas"],
            extraction={"valeur": None, "clarification_needed": True,
                        "clarification_question": "Peux-tu préciser la condition ?"},
        )
        self.assertEqual(profil["mobilite"], "je ne sais pas")
        self.assertIn("Peux-tu préciser la condition ?", sortie)
        self.assertFalse(any("J’ai compris" in p for p in prompts))
        appel.assert_called_once()

    def test_indisponibilite(self):
        for erreur in (ImportError("dépendance absente"), RuntimeError("FAUX_SECRET")):
            with self.subTest(erreur=type(erreur).__name__):
                profil, _, _, sortie, _ = self.parcours(
                    ["Je veux rester ici", "non"], erreur=erreur,
                )
                self.assertEqual(profil["mobilite"], "non")
                self.assertIn("Écris oui, non ou je ne sais pas", sortie)
                self.assertNotIn("FAUX_SECRET", sortie)
        profil, _, _, sortie, _ = self.parcours(
            ["Je veux rester ici", "non"],
            extraction={"valeur": None, "clarification_needed": True,
                        "clarification_question": "Interprétation indisponible."},
        )
        self.assertEqual(profil["mobilite"], "non")
        self.assertIn("Tu peux répondre : oui, non ou je ne sais pas", sortie)

    def test_corrections_et_dependances(self):
        profil, etat, _, _, appel = self.parcours(
            [" OUI ", "Fès"],
            corrections=["non", "5", "Je veux rester ici", "oui"],
            extraction={"valeur": "non", "clarification_needed": False,
                        "clarification_question": None},
        )
        self.assertEqual(profil["mobilite"], "non")
        self.assertIsNone(profil["autres_villes"])
        self.assertNotIn("autres_villes", etat["reponses"])
        appel.assert_called_once()
        profil, _, _, _, appel = self.parcours(
            ["non"], corrections=["non", "5", "Je peux partir", "oui", "Tanger"],
            extraction={"valeur": "oui", "clarification_needed": False,
                        "clarification_question": None},
        )
        self.assertEqual(profil["autres_villes"], "Tanger")
        appel.assert_called_once()

    def test_choix_classiques_sans_api(self):
        for valeur, suite in (("oui", ["Fès"]), ("non", []), ("je ne sais pas", [])):
            with self.subTest(valeur=valeur):
                profil, _, prompts, _, appel = self.parcours([valeur, *suite])
                self.assertEqual(profil["mobilite"], valeur)
                appel.assert_not_called()
                self.assertFalse(any("J’ai compris" in p for p in prompts))


if __name__ == "__main__":
    unittest.main()
