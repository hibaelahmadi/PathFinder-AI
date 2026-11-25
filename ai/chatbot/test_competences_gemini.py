import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from ai.chatbot import competences_gemini as module


class CompetencesTests(unittest.TestCase):
    codes = ["competence_fictive_a", "competence_fictive_b"]

    def sortie(self, codes):
        return json.dumps({"codes": codes, "clarification_needed": not bool(codes),
                           "clarification_question": None if codes else "Que sais-tu déjà faire ?"})

    def test_competence_declaree_et_originaux(self):
        texte = "  Je sais déjà programmer.  "
        with patch.object(module, "_generer_competences", return_value=self.sortie([self.codes[0]])):
            resultat = module.extraire_competences(texte, self.codes)
        self.assertEqual(resultat["codes"], [self.codes[0]])
        self.assertEqual(resultat["original_text"], texte)
        self.assertEqual(resultat["errors"], [])

    def test_souhait_et_incertitude_sans_categorie(self):
        for texte in ("je veux apprendre à coder", "Je ne sais pas", "Je ne sais pas programmer"):
            with self.subTest(texte=texte), patch.object(module, "_generer_competences", return_value=self.sortie([])):
                resultat = module.extraire_competences(texte, self.codes)
                self.assertEqual(resultat["codes"], [])
                self.assertTrue(resultat["clarification_needed"])
        with patch.object(module, "_generer", return_value=self.sortie([])) as appel:
            module._generer_competences("je veux apprendre à coder", self.codes)
        self.assertIn("ne prouve pas", appel.call_args.kwargs["instruction"])

    def test_invente_et_erreur_controles(self):
        for sortie in (self.sortie(["code_invente_fictif"]), "pas JSON", RuntimeError("FAUX_SECRET")):
            with self.subTest(sortie=type(sortie).__name__):
                kwargs = {"side_effect": sortie} if isinstance(sortie, Exception) else {"return_value": sortie}
                with patch.object(module, "_generer_competences", **kwargs):
                    resultat = module.extraire_competences("Original", self.codes)
                self.assertEqual(resultat["codes"], [])
                self.assertEqual(resultat["original_text"], "Original")
                self.assertTrue(resultat["errors"])
                self.assertNotIn("FAUX_SECRET", str(resultat))

    def parcours(self, texte, sorties, corrections=(), activer=True):
        source = Path(__file__).with_name("chatbot.py")
        local = source.with_name("profil_test.json")
        avant = local.read_bytes() if local.exists() else None
        valeurs = iter(["Sciences", "Rabat", "informatique", "programmation", "non",
                        "ingénierie", texte, "0", "privé", *corrections, "oui"])
        affichage = io.StringIO()
        with tempfile.TemporaryDirectory(prefix="pathfinder-competences-") as tmp:
            script = Path(tmp) / "chatbot.py"
            script.write_bytes(source.read_bytes())
            cible = script.with_name("profil_test.json")

            def saisir(prompt):
                self.assertFalse(cible.exists(), "Sauvegarde avant confirmation")
                return next(valeurs)

            with patch.dict(sys.modules, {"competences_gemini": module}), \
                    patch.object(sys, "path", [str(source.parent), *sys.path]), \
                    patch.object(module, "_generer_competences", side_effect=sorties) as appel, \
                    patch("builtins.input", side_effect=saisir), contextlib.redirect_stdout(affichage):
                terminal = runpy.run_path(str(script), run_name="competences_test")
                terminal["main"](codes_competences=self.codes if activer else None)
            profil = json.loads(cible.read_text(encoding="utf-8"))
            self.assertTrue(profil["confirme"])
            self.assertIsNone(next(valeurs, None))
        self.assertEqual(local.read_bytes() if local.exists() else None, avant)
        return profil, appel, affichage.getvalue()

    def test_terminal_confirmation_et_correction(self):
        profil, appel, affichage = self.parcours(
            "  Je sais programmer  ", [self.sortie([self.codes[0]]), self.sortie([self.codes[1]])],
            corrections=["non", "8", "  Je sais dessiner  "],
        )
        self.assertEqual(profil["categories_competences"], [self.codes[1]])
        self.assertEqual(profil["competences_texte_original"], "  Je sais dessiner  ")
        self.assertEqual(appel.call_count, 2)
        self.assertIn("Catégories de compétences déclarées proposées", affichage)

    def test_terminal_vide_incertain_souhait_echec(self):
        for texte, sorties in (("", []), ("Je ne sais pas", [self.sortie([])]),
                               ("je veux apprendre à coder", [self.sortie([])]),
                               ("Je sais coder", [RuntimeError("FAUX_SECRET")])):
            with self.subTest(texte=texte):
                profil, appel, affichage = self.parcours(texte, sorties)
                self.assertIsNone(profil["categories_competences"])
                self.assertEqual(profil["competences_texte_original"], texte)
                self.assertNotIn("FAUX_SECRET", affichage)
                self.assertEqual(appel.call_count, int(bool(texte)))

    def test_correction_vide_ou_echec_efface_categories(self):
        for texte, suite in (("", []), ("Je ne sais pas", [self.sortie([])]),
                              ("Autre réponse", [RuntimeError("FAUX_SECRET")])):
            with self.subTest(texte=texte):
                profil, _, _ = self.parcours(
                    "Je sais coder", [self.sortie([self.codes[0]]), *suite],
                    corrections=["non", "8", texte],
                )
                self.assertIsNone(profil["categories_competences"])

    def test_sans_codes_pas_extraction(self):
        profil, appel, _ = self.parcours("Je sais coder", [], activer=False)
        appel.assert_not_called()
        self.assertNotIn("categories_competences", profil)


if __name__ == "__main__":
    unittest.main()
