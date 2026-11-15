import unittest

from questionnaire import prochaine_question, traiter_reponse


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


if __name__ == "__main__":
    unittest.main()
