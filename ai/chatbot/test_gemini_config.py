"""Tests hors ligne ; uniquement des valeurs fictives, sans affichage de clé."""

import os
from pathlib import Path
import types
import unittest
from unittest.mock import Mock, patch

from ai.chatbot.gemini_config import charger_cle_gemini


class GeminiConfigTests(unittest.TestCase):
    def test_environnement_prioritaire_sans_lecture_dotenv(self):
        lecteur = Mock(side_effect=AssertionError("Lecture inattendue du fichier"))
        with patch.dict(os.environ, {"GEMINI_API_KEY": "  fictive-env  "}), \
                patch.dict("sys.modules", {"dotenv": types.SimpleNamespace(dotenv_values=lecteur)}):
            self.assertTrue(charger_cle_gemini() == "fictive-env")
            lecteur.assert_not_called()

    def test_repli_environnement_absent_ou_vide(self):
        for valeur in (None, "", "   "):
            with self.subTest(cas="absent" if valeur is None else "vide"):
                lecteur = Mock(return_value={"GEMINI_API_KEY": "  fictive-fichier  "})
                with patch.dict(os.environ, {}, clear=True), \
                        patch.dict("sys.modules", {"dotenv": types.SimpleNamespace(dotenv_values=lecteur)}):
                    if valeur is not None:
                        os.environ["GEMINI_API_KEY"] = valeur
                    self.assertTrue(charger_cle_gemini() == "fictive-fichier")
                    self.assertEqual(lecteur.call_count, 1)
                    self.assertEqual(lecteur.call_args.args[0].name, ".env")
                    self.assertEqual(lecteur.call_args.args[0], Path(__file__).resolve().parents[2] / ".env")
                    self.assertEqual(lecteur.call_args.kwargs,
                                     {"interpolate": False, "encoding": "utf-8-sig"})

    def test_absence_totale_erreur_sans_secret(self):
        with patch.dict(os.environ, {}, clear=True), \
                patch.dict("sys.modules", {"dotenv": types.SimpleNamespace(dotenv_values=Mock(return_value={}))}):
            with self.assertRaises(ValueError):
                charger_cle_gemini()

    def test_environnement_non_modifie(self):
        lecteur = Mock(return_value={"GEMINI_API_KEY": "fictive-fichier"})
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "AUTRE_SECRET": "fictif"}, clear=True), \
                patch.dict("sys.modules", {"dotenv": types.SimpleNamespace(dotenv_values=lecteur)}):
            avant = dict(os.environ)
            charger_cle_gemini()
            self.assertTrue(dict(os.environ) == avant)
