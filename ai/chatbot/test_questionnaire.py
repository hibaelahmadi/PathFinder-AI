import unittest

from questionnaire import corriger_reponse, prochaine_question, traiter_reponse


class TraiterReponseTests(unittest.TestCase):
    def avant_mobilite(self):
        return {
            "bac": "Sciences",
            "ville_souhaitee": "Rabat",
            "interets": "informatique",
            "precision_interets": "programmation",
        }

    def assert_erreur_sans_modification(self, reponses, code, texte):
        initiales = reponses.copy()
        resultat = traiter_reponse(reponses, code, texte)
        self.assertTrue(resultat["errors"])
        self.assertEqual(reponses, initiales)
        self.assertEqual(resultat["reponses"], initiales)
        self.assertIsNot(resultat["reponses"], reponses)
        self.assertEqual(resultat["next_question"], prochaine_question(initiales))
        self.assertEqual(
            resultat["ready_for_confirmation"],
            prochaine_question(initiales) is None,
        )

    def test_reponse_normale(self):
        reponses = {}
        resultat = traiter_reponse(reponses, "bac", "  Sciences  ")
        self.assertEqual(resultat["reponses"], {"bac": "Sciences"})
        self.assertEqual(reponses, {})
        self.assertEqual(resultat["next_question"]["question_code"], "ville_souhaitee")
        self.assertFalse(resultat["ready_for_confirmation"])
        self.assertEqual(resultat["errors"], [])

    def test_mobilite_invalide(self):
        for texte in ("peut-être", "", "   "):
            with self.subTest(texte=texte):
                self.assert_erreur_sans_modification(
                    self.avant_mobilite(), "mobilite", texte
                )

    def test_mobilite_normalisee_et_question_adaptee(self):
        for texte, valeur, suivante in (
            (" OUI ", "oui", "autres_villes"),
            (" NON ", "non", "objectif"),
            (" Je Ne Sais Pas ", "je ne sais pas", "objectif"),
        ):
            with self.subTest(texte=texte):
                reponses = self.avant_mobilite()
                resultat = traiter_reponse(reponses, "mobilite", texte)
                self.assertEqual(resultat["errors"], [])
                self.assertEqual(resultat["reponses"]["mobilite"], valeur)
                self.assertEqual(resultat["next_question"]["question_code"], suivante)
                self.assertNotIn("mobilite", reponses)

    def test_mauvais_code(self):
        self.assert_erreur_sans_modification({}, "ville_souhaitee", "Rabat")

    def test_reponse_non_textuelle(self):
        for texte in (None, 42, [], {}):
            with self.subTest(texte=texte):
                self.assert_erreur_sans_modification({}, "bac", texte)

    def test_champ_vide_est_traite(self):
        resultat = traiter_reponse({}, "bac", " \t ")
        self.assertEqual(resultat["reponses"], {"bac": None})
        self.assertEqual(resultat["next_question"]["question_code"], "ville_souhaitee")
        self.assertEqual(resultat["errors"], [])

    def test_fin_du_questionnaire(self):
        reponses = self.avant_mobilite()
        reponses.update(mobilite="non", objectif=None)
        resultat = traiter_reponse(reponses, "competences_declarees", " aider ")
        self.assertEqual(resultat["reponses"]["competences_declarees"], "aider")
        self.assertNotIn("competences_declarees", reponses)
        self.assertIsNone(resultat["next_question"])
        self.assertTrue(resultat["ready_for_confirmation"])
        self.assertEqual(resultat["errors"], [])
        self.assertNotIn("confirme", resultat["reponses"])
        self.assert_erreur_sans_modification(
            resultat["reponses"], "competences_declarees", "créer"
        )


class CorrigerReponseTests(unittest.TestCase):
    def setUp(self):
        self.reponses = {
            "bac": "Sciences",
            "ville_souhaitee": "Rabat",
            "interets": "informatique",
            "precision_interets": "programmation",
            "mobilite": "oui",
            "autres_villes": "Fès",
            "objectif": "ingénierie",
            "competences_declarees": None,
        }
        self.initiales = self.reponses.copy()

    def tearDown(self):
        self.assertEqual(self.reponses, self.initiales)

    def test_interets_redemandent_une_precision(self):
        resultat = corriger_reponse(self.reponses, "interets", " biologie ")
        attendues = self.reponses.copy()
        attendues["interets"] = "biologie"
        del attendues["precision_interets"]
        self.assertEqual(resultat["reponses"], attendues)
        self.assertEqual(resultat["answer_codes_to_delete"], ["precision_interets"])
        self.assertEqual(resultat["next_question"]["question_code"], "precision_interets")
        self.assertIn("biologie", resultat["next_question"]["question_text"])
        self.assertFalse(resultat["ready_for_confirmation"])
        self.assertEqual(resultat["errors"], [])
        suite = traiter_reponse(resultat["reponses"], "precision_interets", "santé")
        self.assertTrue(suite["ready_for_confirmation"])
        self.assertNotIn("confirme", suite["reponses"])

    def test_mobilite_oui_vers_non(self):
        resultat = corriger_reponse(self.reponses, "mobilite", " NON ")
        attendues = self.reponses.copy()
        attendues["mobilite"] = "non"
        del attendues["autres_villes"]
        self.assertEqual(resultat["reponses"], attendues)
        self.assertEqual(resultat["answer_codes_to_delete"], ["autres_villes"])
        self.assertIsNone(resultat["next_question"])
        self.assertTrue(resultat["ready_for_confirmation"])
        self.assertEqual(resultat["errors"], [])

    def test_mobilite_non_vers_oui(self):
        reponses = dict(self.reponses, mobilite="non")
        del reponses["autres_villes"]
        initiales = reponses.copy()
        resultat = corriger_reponse(reponses, "mobilite", " OUI ")
        self.assertEqual(reponses, initiales)
        self.assertEqual(resultat["reponses"], dict(initiales, mobilite="oui"))
        self.assertEqual(resultat["answer_codes_to_delete"], [])
        self.assertEqual(resultat["next_question"]["question_code"], "autres_villes")
        self.assertFalse(resultat["ready_for_confirmation"])
        self.assertEqual(resultat["errors"], [])

    def test_reponse_inchangee_conserve_dependances(self):
        for code, texte in (("interets", " informatique "), ("mobilite", " OUI ")):
            with self.subTest(code=code):
                resultat = corriger_reponse(self.reponses, code, texte)
                self.assertEqual(resultat["reponses"], self.reponses)
                self.assertIsNot(resultat["reponses"], self.reponses)
                self.assertEqual(resultat["answer_codes_to_delete"], [])
                self.assertEqual(resultat["errors"], [])
                self.assertTrue(resultat["ready_for_confirmation"])

    def test_corrections_invalides_preservent_tout(self):
        for code, texte in (("mobilite", "peut-être"), ("bac", None),
                            ("bac", 42), ("inconnu", "texte"),
                            ("confirme", "oui")):
            with self.subTest(code=code, texte=texte):
                resultat = corriger_reponse(self.reponses, code, texte)
                self.assertEqual(resultat["reponses"], self.reponses)
                self.assertIsNot(resultat["reponses"], self.reponses)
                self.assertTrue(resultat["errors"])
                self.assertEqual(resultat["answer_codes_to_delete"], [])
                self.assertIsNone(resultat["next_question"])
                self.assertTrue(resultat["ready_for_confirmation"])

    def test_question_non_traitee_refusee(self):
        resultat = corriger_reponse({}, "bac", "Sciences")
        self.assertEqual(resultat["reponses"], {})
        self.assertTrue(resultat["errors"])
        self.assertEqual(resultat["answer_codes_to_delete"], [])
        self.assertFalse(resultat["ready_for_confirmation"])

    def test_autres_villes_refusees_sans_mobilite(self):
        for mobilite in ("non", "je ne sais pas"):
            with self.subTest(mobilite=mobilite):
                reponses = dict(self.reponses, mobilite=mobilite)
                resultat = corriger_reponse(reponses, "autres_villes", "Tanger")
                self.assertEqual(resultat["reponses"], reponses)
                self.assertEqual(reponses, dict(self.reponses, mobilite=mobilite))
                self.assertTrue(resultat["errors"])
                self.assertEqual(resultat["answer_codes_to_delete"], [])

    def test_champ_vide_et_dependance_vide(self):
        resultat = corriger_reponse(self.reponses, "objectif", "   ")
        self.assertEqual(resultat["reponses"], dict(self.reponses, objectif=None))
        self.assertEqual(resultat["errors"], [])
        self.assertEqual(resultat["answer_codes_to_delete"], [])
        reponses = dict(self.reponses, precision_interets=None)
        resultat = corriger_reponse(reponses, "interets", "biologie")
        self.assertEqual(resultat["answer_codes_to_delete"], ["precision_interets"])
        self.assertIsNone(reponses["precision_interets"])


if __name__ == "__main__":
    unittest.main()
