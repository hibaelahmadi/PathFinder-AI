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


class InteretsTerminalTests(unittest.TestCase):
    codes = ["interet_fictif_a", "interet_fictif_b"]

    def clair(self, code):
        return {"codes": [code], "clarification_needed": False,
                "clarification_question": None, "errors": []}

    def vague(self):
        return {"codes": [], "clarification_needed": True,
                "clarification_question": "Quelle activité précise préfères-tu ?", "errors": []}

    def parcours(self, sorties, corrections=(), codes=True):
        source = Path(__file__).with_name("chatbot.py")
        local = source.with_name("profil_test.json")
        avant = local.read_bytes() if local.exists() else None
        module = types.ModuleType("interets_gemini")
        module.extraire_interets = Mock(side_effect=sorties)
        textes = iter(["Sciences", "Rabat", "  Un peu de tout  ", "  Créer des jeux  ",
                       "non", "ingénierie", "", "0", "privé", *corrections, "oui"])
        prompts, affichage = [], io.StringIO()
        with tempfile.TemporaryDirectory(prefix="pathfinder-interets-") as tmp:
            script = Path(tmp) / "chatbot.py"
            script.write_bytes(source.read_bytes())
            cible = script.with_name("profil_test.json")

            def saisir(prompt):
                self.assertFalse(cible.exists())
                prompts.append(prompt)
                return next(textes)

            with patch.dict(sys.modules, {"interets_gemini": module}), \
                    patch.object(sys, "path", [str(source.parent), *sys.path]), \
                    patch("builtins.input", side_effect=saisir), contextlib.redirect_stdout(affichage):
                terminal = runpy.run_path(str(script), run_name="interets_test")
                terminal["main"](codes_interets=self.codes if codes else None)
            profil = json.loads(cible.read_text(encoding="utf-8"))
            self.assertTrue(profil["confirme"])
            self.assertIsNone(next(textes, None))
        self.assertEqual(local.read_bytes() if local.exists() else None, avant)
        return profil, module.extraire_interets, prompts, affichage.getvalue()

    def test_clair_et_originaux_conserves(self):
        profil, appel, _, sortie = self.parcours([self.clair(self.codes[0])])
        self.assertEqual(profil["categories_interets"], [self.codes[0]])
        self.assertEqual(profil["interets_texte_original"], "  Un peu de tout  ")
        self.assertEqual(profil["precision_interets_texte_original"], "  Créer des jeux  ")
        self.assertIn("Catégories d'intérêts proposées", sortie)
        appel.assert_called_once()

    def test_clarification_remplace_relance_et_combine(self):
        profil, appel, prompts, _ = self.parcours([self.vague(), self.clair(self.codes[0])])
        self.assertEqual(profil["categories_interets"], [self.codes[0]])
        self.assertEqual(prompts.count(self.vague()["clarification_question"]), 1)
        self.assertEqual(appel.call_count, 2)
        combine = appel.call_args.args[0]
        self.assertIn("  Un peu de tout  ", combine)
        self.assertIn("  Créer des jeux  ", combine)

    def test_encore_vague_aucune_deuxieme_relance(self):
        profil, appel, prompts, _ = self.parcours([self.vague(), self.vague()])
        self.assertIsNone(profil["categories_interets"])
        self.assertEqual(appel.call_count, 2)
        self.assertEqual(prompts.count(self.vague()["clarification_question"]), 1)

    def test_indisponibilite_continue(self):
        profil, appel, _, _ = self.parcours([RuntimeError("FAUX_SECRET")])
        self.assertIsNone(profil["categories_interets"])
        appel.assert_called_once()

    def test_correction_recalcule_et_efface_ancien_resultat(self):
        for nouvelle in (self.clair(self.codes[1]), {"errors": ["indisponible"]}):
            with self.subTest(nouvelle=nouvelle):
                profil, appel, _, _ = self.parcours(
                    [self.clair(self.codes[0]), nouvelle],
                    corrections=["non", "3", "Autre intérêt", "Nouvelle précision"],
                )
                self.assertEqual(profil["categories_interets"], nouvelle.get("codes"))
                self.assertEqual(profil["interets_texte_original"], "Autre intérêt")
                self.assertEqual(appel.call_count, 2)

    def test_sans_codes_aucun_appel_ni_champ_supplementaire(self):
        profil, appel, _, _ = self.parcours([], codes=False)
        appel.assert_not_called()
        self.assertNotIn("categories_interets", profil)


if __name__ == "__main__":
    unittest.main()
