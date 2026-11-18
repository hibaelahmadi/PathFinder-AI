import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from ai.chatbot import objectif_gemini as module


class ObjectifTests(unittest.TestCase):
    codes = ["metier_fictif_a", "metier_fictif_b"]

    def sortie(self, codes):
        return json.dumps({"codes": codes, "clarification_needed": not bool(codes),
                           "clarification_question": None if codes else "Un métier précis ?"})

    def test_metier_clair(self):
        texte = "  Je veux exercer le métier indiqué.  "
        with patch.object(module, "_generer_objectif", return_value=self.sortie([self.codes[0]])):
            resultat = module.extraire_objectif(texte, self.codes)
        self.assertEqual(resultat["code_metier"], self.codes[0])
        self.assertEqual(resultat["original_text"], texte)
        self.assertEqual(resultat["errors"], [])

    def test_indecision_et_domaine_general(self):
        for texte in ("je ne sais pas", "J'hésite entre deux métiers", "La santé m'intéresse"):
            with self.subTest(texte=texte), patch.object(module, "_generer_objectif", return_value=self.sortie([])):
                resultat = module.extraire_objectif(texte, self.codes)
                self.assertIsNone(resultat["code_metier"])
                self.assertTrue(resultat["clarification_needed"])
                self.assertEqual(resultat["errors"], [])

    def test_plusieurs_codes_inventes_ou_json_invalide(self):
        for sortie in (self.sortie(self.codes), self.sortie(["metier_invente_fictif"]), "pas JSON"):
            with self.subTest(sortie=sortie), patch.object(module, "_generer_objectif", return_value=sortie):
                resultat = module.extraire_objectif("Texte original", self.codes)
                self.assertIsNone(resultat["code_metier"])
                self.assertTrue(resultat["errors"])
                self.assertEqual(resultat["original_text"], "Texte original")

    def test_erreur_controlee_et_vide(self):
        with patch.object(module, "_generer_objectif", side_effect=RuntimeError("FAUX_SECRET")) as appel:
            resultat = module.extraire_objectif("Texte", self.codes)
            appel.assert_called_once()
        self.assertIsNone(resultat["code_metier"])
        self.assertTrue(resultat["errors"])
        self.assertNotIn("FAUX_SECRET", str(resultat))
        with patch.object(module, "_generer_objectif") as appel:
            self.assertIsNone(module.extraire_objectif(" ", self.codes)["code_metier"])
            appel.assert_not_called()

    def parcours(self, objectif, sorties, corrections=(), activer=True):
        source = Path(__file__).with_name("chatbot.py")
        local = source.with_name("profil_test.json")
        avant = local.read_bytes() if local.exists() else None
        valeurs = iter(["Sciences", "Rabat", "informatique", "programmation", "non",
                        objectif, "", "0", "privé", *corrections, "oui"])
        sortie = io.StringIO()
        with tempfile.TemporaryDirectory(prefix="pathfinder-objectif-") as tmp:
            script = Path(tmp) / "chatbot.py"
            script.write_bytes(source.read_bytes())
            cible = script.with_name("profil_test.json")

            def saisir(prompt):
                self.assertFalse(cible.exists(), "Sauvegarde avant confirmation")
                return next(valeurs)

            with patch.dict(sys.modules, {"objectif_gemini": module}), \
                    patch.object(sys, "path", [str(source.parent), *sys.path]), \
                    patch.object(module, "_generer_objectif", side_effect=sorties) as appel, \
                    patch("builtins.input", side_effect=saisir), contextlib.redirect_stdout(sortie):
                terminal = runpy.run_path(str(script), run_name="objectif_test")
                terminal["main"](codes_metiers=self.codes if activer else None)
            profil = json.loads(cible.read_text(encoding="utf-8"))
            self.assertTrue(profil["confirme"])
            self.assertIsNone(next(valeurs, None))
        self.assertEqual(local.read_bytes() if local.exists() else None, avant)
        return profil, appel, sortie.getvalue()

    def test_terminal_correction_recalcule(self):
        profil, appel, sortie = self.parcours(
            "Premier métier", [self.sortie([self.codes[0]]), self.sortie([self.codes[1]])],
            corrections=["non", "7", "  Autre métier  "],
        )
        self.assertEqual(profil["code_metier"], self.codes[1])
        self.assertEqual(profil["objectif_texte_original"], "  Autre métier  ")
        self.assertEqual(appel.call_count, 2)
        self.assertIn("Métier proposé (code)", sortie)

    def test_terminal_non_precis_et_echec(self):
        for texte, sorties in (("je ne sais pas", [self.sortie([])]),
                               ("Deux métiers possibles", [self.sortie([])]),
                               ("Un domaine général", [self.sortie([])]),
                               ("Un métier", [RuntimeError("FAUX_SECRET")]), ("", [])):
            with self.subTest(texte=texte):
                profil, _, sortie = self.parcours(texte, sorties)
                self.assertIsNone(profil["code_metier"])
                self.assertEqual(profil["objectif_texte_original"], texte)
                self.assertNotIn("FAUX_SECRET", sortie)

    def test_correction_indecise_ou_erreur_efface_ancien_metier(self):
        for nouvelle in (self.sortie([]), RuntimeError("FAUX_SECRET")):
            with self.subTest(type=type(nouvelle).__name__):
                profil, _, _ = self.parcours(
                    "Un métier", [self.sortie([self.codes[0]]), nouvelle],
                    corrections=["non", "7", "je ne sais pas"],
                )
                self.assertIsNone(profil["code_metier"])

    def test_sans_codes_aucune_extraction(self):
        profil, appel, _ = self.parcours("Un métier", [], activer=False)
        appel.assert_not_called()
        self.assertNotIn("code_metier", profil)


if __name__ == "__main__":
    unittest.main()
