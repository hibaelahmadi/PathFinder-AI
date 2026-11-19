from copy import deepcopy
import unittest

from ai.chatbot.questionnaire import traiter_questionnaire


class ContratQuestionnaireTests(unittest.TestCase):
    def demarrer(self):
        retour = traiter_questionnaire(None, "start")
        self.assertEqual(retour["errors"], [])
        return retour["etat"]

    def envoyer(self, etat, action, code, texte):
        initial = deepcopy(etat)
        reponse = {"question_code": code, "answer_text": texte,
                   "answer_value": {"faux": [1]}, "question_text": "FAUX"}
        copie = deepcopy(reponse)
        retour = traiter_questionnaire(etat, action, reponse)
        self.assertEqual(etat, initial)
        self.assertEqual(reponse, copie)
        self.assertEqual(retour["errors"], [])
        return retour

    def remplir(self, mobilite="non"):
        etat = self.demarrer()
        textes = [" Sciences ", "Rabat", "informatique", "programmation",
                  mobilite]
        if mobilite == "oui":
            textes.append("Fès")
        textes.extend(["ingénierie", "  "])
        for texte in textes:
            retour = self.envoyer(etat, "answer", etat["expected_question_code"], texte)
            etat = retour["etat"]
        return retour

    def erreur(self, etat, action, reponse=None):
        copie = deepcopy(etat)
        retour = traiter_questionnaire(etat, action, reponse)
        self.assertTrue(retour["errors"])
        self.assertEqual(retour["etat"], copie)
        self.assertEqual(etat, copie)
        self.assertEqual(retour["answers_to_save"], [])
        self.assertEqual(retour["answer_codes_to_delete"], [])
        return retour

    def test_structure_exacte_p2(self):
        etat = {
            "status": "in_progress",
            "expected_question_code": "ville_souhaitee",
            "answers": {
                "bac": {
                    "question_code": "bac",
                    "question_text": "Quelle est ta série de bac ?",
                    "answer_text": "Sciences mathématiques",
                    "answer_value": None,
                }
            },
        }
        reponse = {
            "question_code": "ville_souhaitee",
            "question_text": "Dans quelle ville souhaites-tu étudier ?",
            "answer_text": " Rabat ",
            "answer_value": None,
        }
        initial, originale = deepcopy(etat), deepcopy(reponse)
        retour = traiter_questionnaire(etat, "answer", reponse)
        self.assertEqual(retour["errors"], [])
        self.assertEqual(etat, initial)
        self.assertEqual(reponse, originale)
        self.assertIsInstance(retour["etat"]["answers"], dict)
        self.assertEqual(retour["etat"]["answers"]["bac"]["answer_value"], "Sciences mathématiques")
        self.assertEqual(retour["etat"]["answers"]["ville_souhaitee"]["answer_text"], " Rabat ")
        self.assertEqual(retour["profile"]["ville_souhaitee"], "Rabat")
        self.assertEqual(retour["next_question"]["question_code"], "interets")
        self.assertIsInstance(retour["answers_to_save"], list)
        self.assertIsInstance(retour["answer_codes_to_delete"], list)
        self.erreur(etat, "answer", {"question_code": "mobilite", "answer_text": "oui"})

    def test_cycle_complet(self):
        retour = self.remplir()
        self.assertEqual(retour["etat"]["status"], "in_progress")
        self.assertIsNone(retour["next_question"])
        self.assertFalse(retour["profile_confirmed"])
        self.assertIsNone(retour["profile"]["competences_declarees"])
        for code in ("notes", "budget_annuel_max", "type_etablissement"):
            self.assertIn(code, retour["profile"])
            self.assertIsNone(retour["profile"][code])
            self.assertNotIn(code, retour["etat"]["answers"])
        self.assertEqual(retour["etat"]["answers"]["bac"]["answer_text"], " Sciences ")
        self.assertEqual(retour["etat"]["answers"]["bac"]["answer_value"], "Sciences")
        confirme = traiter_questionnaire(retour["etat"], "confirm")
        self.assertTrue(confirme["profile_confirmed"])
        self.assertTrue(confirme["profile"]["confirme"])
        self.assertEqual(confirme["etat"]["status"], "completed")
        for action in ("answer", "correct"):
            erreur = self.erreur(confirme["etat"], action,
                                 {"question_code": "bac", "answer_text": "autre"})
            self.assertTrue(erreur["profile_confirmed"])
        rouvert = traiter_questionnaire(confirme["etat"], "reopen")
        self.assertEqual(rouvert["errors"], [])
        self.assertEqual(rouvert["etat"]["answers"], confirme["etat"]["answers"])
        self.assertEqual(rouvert["etat"]["status"], "in_progress")
        self.assertFalse(rouvert["profile_confirmed"])
        self.assertFalse(rouvert["profile"]["confirme"])

    def test_ordre_et_metadonnees_client(self):
        etat = self.demarrer()
        etat["expected_question_code"] = "mobilite"
        self.erreur(etat, "answer", {"question_code": "mobilite", "answer_text": "oui"})
        retour = self.envoyer(etat, "answer", "bac", " Sciences ")
        self.assertEqual(retour["next_question"]["question_code"], "ville_souhaitee")
        entree = retour["answers_to_save"][0]
        self.assertEqual(entree["question_text"], "Quelle est ta série de bac ? ")
        self.assertEqual(entree["answer_value"], "Sciences")
        retour["etat"]["answers"]["bac"]["answer_value"] = {"faux": [1]}
        retour["etat"]["answers"]["bac"]["question_text"] = "FAUX"
        suite = self.envoyer(retour["etat"], "answer", "ville_souhaitee", "Rabat")
        self.assertEqual(suite["profile"]["bac"], "Sciences")

    def test_corrections_dependantes(self):
        etat = self.remplir("oui")["etat"]
        retour = self.envoyer(etat, "correct", "interets", "biologie")
        self.assertEqual(retour["answer_codes_to_delete"], ["precision_interets"])
        self.assertEqual(retour["next_question"]["question_code"], "precision_interets")
        self.assertIsNone(retour["profile"]["precision_interets"])
        self.assertIn("biologie", retour["next_question"]["question_text"])
        suite = self.envoyer(retour["etat"], "answer", "precision_interets", "santé")
        retour = self.envoyer(suite["etat"], "correct", "mobilite", "NON")
        self.assertEqual(retour["answer_codes_to_delete"], ["autres_villes"])
        self.assertIsNone(retour["profile"]["autres_villes"])
        retour = self.envoyer(retour["etat"], "correct", "mobilite", "OUI")
        self.assertEqual(retour["answer_codes_to_delete"], [])
        self.assertEqual(retour["next_question"]["question_code"], "autres_villes")
        suite = self.envoyer(retour["etat"], "answer", "autres_villes", "Tanger")
        identique = self.envoyer(suite["etat"], "correct", "mobilite", " oui ")
        self.assertEqual(identique["answer_codes_to_delete"], [])
        self.assertEqual(identique["profile"]["autres_villes"], "Tanger")

    def test_actions_interdites_et_validation(self):
        etat = self.demarrer()
        for action in ("confirm", "reopen", "inconnue"):
            self.erreur(etat, action)
        self.erreur(etat, "correct", {"question_code": "bac", "answer_text": "S"})
        self.erreur(etat, "answer", {"question_code": "bac", "answer_text": None})
        retour = self.envoyer(etat, "answer", "bac", "")
        self.assertIsNone(retour["profile"]["bac"])
        self.assertEqual(retour["next_question"]["question_code"], "ville_souhaitee")
        self.erreur(retour["etat"], "start")
        complet = self.remplir("oui")["etat"]
        erreur = self.erreur(complet, "correct", {"question_code": "mobilite", "answer_text": "peut-être"})
        self.assertFalse(erreur["profile_confirmed"])
        self.assertEqual(erreur["profile"]["autres_villes"], "Fès")

    def test_mobilite_invalide_attendue(self):
        etat = self.demarrer()
        for texte in ("Sciences", "Rabat", "informatique", "programmation"):
            etat = self.envoyer(etat, "answer", etat["expected_question_code"], texte)["etat"]
        self.erreur(etat, "answer", {"question_code": "mobilite", "answer_text": "peut-être"})
        retour = self.envoyer(etat, "answer", "mobilite", " OUI ")
        self.assertEqual(retour["profile"]["mobilite"], "oui")
        self.assertEqual(retour["answers_to_save"][0]["answer_text"], " OUI ")

    def test_etats_stockes_invalides(self):
        for modification in ("cle_incoherente", "inconnu", "mobilite", "inapplicable", "completed"):
            with self.subTest(modification=modification):
                etat = self.remplir()["etat"]
                if modification == "cle_incoherente":
                    etat["answers"]["ville_souhaitee"]["question_code"] = "bac"
                elif modification == "inconnu":
                    etat["answers"]["bac"]["question_code"] = "confirme"
                elif modification == "mobilite":
                    etat["answers"]["mobilite"]["answer_text"] = "peut-être"
                elif modification == "inapplicable":
                    etat["answers"]["autres_villes"] = {"question_code": "autres_villes", "answer_text": "Fès"}
                else:
                    etat["status"] = "completed"
                    etat["answers"].pop("competences_declarees")
                self.erreur(etat, "confirm")

    def test_entrees_malformees_et_copies_profondes(self):
        for etat in ([], {}, {"status": "in_progress", "answers": []},
                     {"status": "in_progress", "answers": [None]},
                     {"status": "in_progress", "answers": [{"question_code": []}]}):
            self.erreur(etat, "answer")
        etat = self.demarrer()
        etat["metadata"] = {"liste": [1]}
        retour = self.erreur(etat, "confirm")
        retour["etat"]["metadata"]["liste"].append(2)
        self.assertEqual(etat["metadata"]["liste"], [1])
        complet = self.remplir()["etat"]
        complet["answers"]["bac"]["answer_value"] = {"liste": [1]}
        retour = self.erreur(complet, "start")
        retour["etat"]["answers"]["bac"]["answer_value"]["liste"].append(2)
        self.assertEqual(complet["answers"]["bac"]["answer_value"], {"liste": [1]})


if __name__ == "__main__":
    unittest.main()
