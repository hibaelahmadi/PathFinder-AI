import unittest

from ai.chatbot.validation_profil import (
    valider_budget_annuel,
    valider_note,
    valider_type_etablissement,
)


class ValidationProfilTests(unittest.TestCase):
    def test_types_etablissement_acceptes(self):
        for texte, valeur in (
            ("public", "public"), (" PUBLIC ", "public"),
            ("privé", "prive"), ("prive", "prive"),
            (" \tPRIVÉ\n", "prive"), (" PrIvE ", "prive"),
            ("sans préférence", None), ("sans preference", None),
            (" SANS PRÉFÉRENCE ", None), (" SANS PREFERENCE ", None),
            ("", None), (" \t\n ", None),
        ):
            with self.subTest(texte=texte):
                self.assertEqual(
                    valider_type_etablissement(texte),
                    {"value": valeur, "errors": []},
                )

    def test_types_etablissement_refuses(self):
        for texte in ("autre", "public ou privé", "sans  preference", "0"):
            with self.subTest(texte=texte):
                self.assert_invalide(valider_type_etablissement, texte)

    def test_types_etablissement_non_textuels(self):
        for texte in (None, 0, 12.5, True, [], {}, b"public"):
            with self.subTest(texte=texte):
                self.assert_invalide(valider_type_etablissement, texte)

    def assert_invalide(self, fonction, texte):
        resultat = fonction(texte)
        self.assertIsNone(resultat["value"])
        self.assertTrue(resultat["errors"])
        self.assertTrue(all(isinstance(message, str) for message in resultat["errors"]))

    def test_bornes_note(self):
        for texte, valeur in (("0", 0), ("20", 20), (" 20.0 ", 20)):
            with self.subTest(texte=texte):
                self.assertEqual(valider_note(texte), {"value": valeur, "errors": []})
        for texte in ("-0.01", "20.01"):
            with self.subTest(texte=texte):
                self.assert_invalide(valider_note, texte)

    def test_bornes_budget(self):
        for texte, valeur in (("0", 0), (" 0,00 ", 0), ("250000", 250000)):
            with self.subTest(texte=texte):
                self.assertEqual(valider_budget_annuel(texte), {"value": valeur, "errors": []})
        self.assert_invalide(valider_budget_annuel, "-0.01")

    def test_decimales(self):
        for fonction in (valider_note, valider_budget_annuel):
            for texte in (" 12,75 ", "12.75"):
                with self.subTest(fonction=fonction.__name__, texte=texte):
                    self.assertEqual(fonction(texte), {"value": 12.75, "errors": []})

    def test_champ_vide(self):
        for fonction in (valider_note, valider_budget_annuel):
            for texte in ("", " \t\n "):
                with self.subTest(fonction=fonction.__name__, texte=texte):
                    self.assertEqual(fonction(texte), {"value": None, "errors": []})

    def test_textes_invalides(self):
        for fonction in (valider_note, valider_budget_annuel):
            for texte in ("bonjour", "12 DH", "12,5.3", "1,2,3", "--2"):
                with self.subTest(fonction=fonction.__name__, texte=texte):
                    self.assert_invalide(fonction, texte)

    def test_mauvais_types(self):
        for fonction in (valider_note, valider_budget_annuel):
            for texte in (None, 0, 12.5, True, [], {}, b"12"):
                with self.subTest(fonction=fonction.__name__, texte=texte):
                    self.assert_invalide(fonction, texte)

    def test_valeurs_non_finies(self):
        for fonction in (valider_note, valider_budget_annuel):
            for texte in ("NaN", "nan", "Infinity", "+inf", "-inf", "1e9999"):
                with self.subTest(fonction=fonction.__name__, texte=texte):
                    self.assert_invalide(fonction, texte)


if __name__ == "__main__":
    unittest.main()
