import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


class VocabulaireTerminalTests(unittest.TestCase):
    categories = {
        "required_subjects": ["matiere_fictive"],
        "interests": ["interet_fictif"],
        "skills": ["competence_fictive"],
        "career_paths": ["metier_fictif"],
    }

    def charger(self, script):
        return runpy.run_path(str(script), run_name="test_vocabulaire")

    def test_lancement_complet_gemini_simule(self):
        source = Path(__file__).with_name("chatbot.py")
        local = source.with_name("profil_test.json")
        avant = local.read_bytes() if local.exists() else None
        import interets_gemini
        import competences_gemini
        import objectif_gemini

        def sortie(code):
            return json.dumps({"codes": [code], "clarification_needed": False,
                               "clarification_question": None})

        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "chatbot.py"
            script.write_bytes(source.read_bytes())
            vocabulaire = Path(tmp) / "vocabulaire test.json"
            vocabulaire.write_text(json.dumps({"categories": self.categories}), encoding="utf-8")
            cible = script.with_name("profil_test.json")
            textes = iter(["Sciences", "Rabat", "  Créer des programmes  ",
                           "Des jeux", "non", "  Métier fictif  ",
                           "  Je sais coder  ", "0", "privé", "0", "oui"])

            def repondre(question):
                self.assertFalse(cible.exists())
                return next(textes)

            with patch.object(sys, "path", [str(source.parent), *sys.path]), \
                    patch.object(sys, "argv", [str(script), "--vocabulaire", str(vocabulaire)]), \
                    patch("builtins.input", side_effect=repondre), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    patch.object(interets_gemini, "_generer", return_value=sortie("interet_fictif")) as interets, \
                    patch.object(competences_gemini, "_generer_competences", return_value=sortie("competence_fictive")) as competences, \
                    patch.object(objectif_gemini, "_generer_objectif", return_value=sortie("metier_fictif")) as metier:
                runpy.run_path(str(script), run_name="__main__")
            profil = json.loads(cible.read_text(encoding="utf-8"))
            self.assertTrue(profil["confirme"])
            self.assertEqual(profil["notes"], {"matiere_fictive": 0})
            self.assertEqual(profil["budget_annuel_max"], 0)
            self.assertEqual(profil["type_etablissement"], "prive")
            self.assertEqual(profil["categories_interets"], ["interet_fictif"])
            self.assertEqual(profil["categories_competences"], ["competence_fictive"])
            self.assertEqual(profil["code_metier"], "metier_fictif")
            self.assertEqual(profil["interets_texte_original"], "  Créer des programmes  ")
            for appel, cle in ((interets, "interests"), (competences, "skills"), (metier, "career_paths")):
                appel.assert_called_once()
                self.assertEqual(appel.call_args.args[1], self.categories[cle])
            self.assertIsNone(next(textes, None))
        self.assertEqual(local.read_bytes() if local.exists() else None, avant)

    def test_sans_option(self):
        lancer = self.charger(Path(__file__).with_name("chatbot.py"))["lancer_terminal"]
        with patch.dict(lancer.__globals__, {"main": Mock(return_value="ok")}):
            self.assertEqual(lancer([]), "ok")
            lancer.__globals__["main"].assert_called_once_with()

    def test_fichier_absent_ou_invalide(self):
        lancer = self.charger(Path(__file__).with_name("chatbot.py"))["lancer_terminal"]
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "vocabulaire.json"
            invalides = [None, "{", "[]", '{}',
                         json.dumps({"categories": {**self.categories, "skills": "incorrect"}}),
                         json.dumps({"categories": {**self.categories, "skills": [1]}}),
                         json.dumps({"categories": {**self.categories, "skills": [" "]}}),
                         json.dumps({"categories": {**self.categories, "skills": ["a", "a"]}})]
            for contenu in invalides:
                with self.subTest(contenu=contenu):
                    if contenu is not None:
                        chemin.write_text(contenu, encoding="utf-8")
                    erreur = io.StringIO()
                    entree = Mock()
                    with patch("builtins.input", entree), contextlib.redirect_stderr(erreur):
                        with self.assertRaises(SystemExit) as sortie:
                            lancer(["--vocabulaire", str(chemin)])
                    self.assertEqual(sortie.exception.code, 2)
                    self.assertIn(str(chemin), erreur.getvalue())
                    entree.assert_not_called()


if __name__ == "__main__":
    unittest.main()
