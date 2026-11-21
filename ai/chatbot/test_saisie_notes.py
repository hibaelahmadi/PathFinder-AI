import contextlib
import io
import unittest
from unittest.mock import patch

from ai.chatbot.saisie_notes import saisir_notes


class SaisieNotesTests(unittest.TestCase):
    def test_correction_ne_modifie_pas_notes_existantes(self):
        notes = {"matiere_fictive_a": 0, "matiere_fictive_b": 12}
        with patch("builtins.input", side_effect=["", "effacer"]), contextlib.redirect_stdout(io.StringIO()):
            resultat = saisir_notes(
                ["matiere_fictive_a", "matiere_fictive_b"], notes, correction=True
            )
        self.assertEqual(resultat, {"matiere_fictive_a": 0})
        self.assertEqual(notes, {"matiere_fictive_a": 0, "matiere_fictive_b": 12})

    def test_ignore_vide_conserve_zero_et_decimale(self):
        matieres = ["matiere_fictive_a", "matiere_fictive_b", "matiere_fictive_c"]
        initiales = matieres.copy()
        with patch("builtins.input", side_effect=["", "0", " 12,5 "]) as saisie:
            notes = saisir_notes(matieres)
        self.assertEqual(notes, {"matiere_fictive_b": 0, "matiere_fictive_c": 12.5})
        self.assertIsInstance(notes["matiere_fictive_b"], (int, float))
        self.assertEqual(matieres, initiales)
        self.assertEqual(saisie.call_count, 3)

    def test_note_invalide_redemandee_sur_la_meme_matiere(self):
        sortie = io.StringIO()
        with patch("builtins.input", side_effect=["21", "NaN", "texte", "20"]) as saisie, contextlib.redirect_stdout(sortie):
            notes = saisir_notes(["matiere_fictive_a"])
        self.assertEqual(notes, {"matiere_fictive_a": 20})
        self.assertEqual(saisie.call_count, 4)
        self.assertTrue(all(a.args == saisie.call_args_list[0].args for a in saisie.call_args_list))
        self.assertIn("entre 0 et 20", sortie.getvalue())
        self.assertIn("doit être fini", sortie.getvalue())
        self.assertIn("doit être un nombre", sortie.getvalue())

    def test_toutes_matieres_ignorees(self):
        with patch("builtins.input", side_effect=["", "   "]):
            self.assertIsNone(saisir_notes(["matiere_fictive_a", "matiere_fictive_b"]))

    def test_aucune_matiere(self):
        with patch("builtins.input") as saisie:
            self.assertIsNone(saisir_notes([]))
            saisie.assert_not_called()

    def test_liste_invalide_refusee_avant_saisie(self):
        for matieres in (None, "matiere_fictive_a", [None], [" "],
                         ["matiere_fictive_a", "matiere_fictive_a"]):
            with self.subTest(matieres=matieres), patch("builtins.input") as saisie:
                with self.assertRaises(ValueError):
                    saisir_notes(matieres)
                saisie.assert_not_called()


if __name__ == "__main__":
    unittest.main()
