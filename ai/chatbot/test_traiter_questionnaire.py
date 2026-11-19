from copy import deepcopy
import unittest

from ai.chatbot.questionnaire import traiter_questionnaire


class ContratQuestionnaireTests(unittest.TestCase):
    def appel_budget_type(self, etat, action, code=None, texte=None):
        reponse = None if code is None else {
            "question_code": code, "answer_text": texte,
            "answer_value": "valeur client ignorée", "question_text": "FAUX",
        }
        initial, initial_reponse = deepcopy(etat), deepcopy(reponse)
        retour = traiter_questionnaire(
            etat, action, reponse, inclure_budget_type=True,
        )
        self.assertEqual(etat, initial)
        self.assertEqual(reponse, initial_reponse)
        return retour

    def test_mode_budget_type_cycle_correction_confirmation(self):
        retour = traiter_questionnaire(None, "start", inclure_budget_type=True)
        for texte in ["Sciences", "Rabat", "informatique", "jeux", "non", "ingénierie", "Python"]:
            retour = self.appel_budget_type(retour["etat"], "answer",
                                           retour["next_question"]["question_code"], texte)
            self.assertFalse(retour["errors"])
        self.assertEqual(retour["next_question"]["question_code"], "budget_annuel_max")
        refuse = self.appel_budget_type(retour["etat"], "confirm")
        self.assertTrue(refuse["errors"])
        self.assertEqual(refuse["etat"], retour["etat"])
        retour = self.appel_budget_type(retour["etat"], "answer", "budget_annuel_max", " 0 ")
        self.assertEqual(retour["profile"]["budget_annuel_max"], 0)
        self.assertIsInstance(retour["profile"]["budget_annuel_max"], (int, float))
        self.assertEqual(retour["answers_to_save"][0]["answer_text"], " 0 ")
        self.assertEqual(retour["answers_to_save"][0]["answer_value"], 0)
        self.assertEqual(retour["next_question"]["question_code"], "type_etablissement")
        retour = self.appel_budget_type(retour["etat"], "answer", "type_etablissement", " PRIVÉ ")
        self.assertEqual(retour["profile"]["type_etablissement"], "prive")
        self.assertEqual(retour["etat"]["answers"]["type_etablissement"]["answer_text"], " PRIVÉ ")
        self.assertEqual(retour["answers_to_save"][0]["answer_value"], "prive")
        self.assertIsNone(retour["next_question"])
        self.assertFalse(retour["profile_confirmed"])
        for code, texte, valeur in [("budget_annuel_max", "12,5", 12.5),
                                     ("type_etablissement", "public", "public"),
                                     ("budget_annuel_max", "", None),
                                     ("type_etablissement", "  ", None),
                                     ("budget_annuel_max", "0", 0),
                                     ("type_etablissement", "privé", "prive")]:
            retour = self.appel_budget_type(retour["etat"], "correct", code, texte)
            self.assertFalse(retour["errors"])
            self.assertEqual(retour["profile"][code], valeur)
            self.assertEqual(retour["answers_to_save"][0]["answer_value"], valeur)
        retour = self.appel_budget_type(retour["etat"], "confirm")
        self.assertFalse(retour["errors"])
        self.assertTrue(retour["profile_confirmed"])
        self.assertEqual(retour["etat"]["status"], "completed")

    def test_mode_budget_type_erreurs_et_champs_vides(self):
        etat = self.remplir()["etat"]
        for action, code, texte in [("answer", "type_etablissement", "public"),
                                     ("correct", "budget_annuel_max", "0"),
                                     ("answer", "budget_annuel_max", "-1"),
                                     ("answer", "budget_annuel_max", "NaN"),
                                     ("answer", "budget_annuel_max", 0)]:
            erreur = self.appel_budget_type(etat, action, code, texte)
            self.assertTrue(erreur["errors"])
            self.assertEqual(erreur["etat"], etat)
            self.assertEqual(erreur["answers_to_save"], [])
            self.assertEqual(erreur["answer_codes_to_delete"], [])
        retour = self.appel_budget_type(etat, "answer", "budget_annuel_max", "")
        self.assertIsNone(retour["profile"]["budget_annuel_max"])
        erreur = self.appel_budget_type(retour["etat"], "answer", "type_etablissement", "autre")
        self.assertTrue(erreur["errors"])
        self.assertEqual(erreur["etat"], retour["etat"])
        retour = self.appel_budget_type(retour["etat"], "answer", "type_etablissement", "")
        self.assertIsNone(retour["profile"]["type_etablissement"])
        erreur = self.appel_budget_type(retour["etat"], "correct", "budget_annuel_max", "inf")
        self.assertTrue(erreur["errors"])
        self.assertEqual(erreur["etat"], retour["etat"])

    def test_ancienne_session_confirmee_avec_et_sans_mode(self):
        ancien = traiter_questionnaire(self.remplir()["etat"], "confirm")
        for mode in (False, True):
            retour = traiter_questionnaire(ancien["etat"], "confirm", inclure_budget_type=mode)
            self.assertTrue(retour["profile_confirmed"])
            self.assertEqual(retour["profile"], ancien["profile"])
            self.assertIsNone(retour["next_question"])
            self.assertEqual(retour["etat"], ancien["etat"])
        rouvert = self.appel_budget_type(ancien["etat"], "reopen")
        self.assertFalse(rouvert["errors"])
        self.assertFalse(rouvert["profile_confirmed"])
        self.assertEqual(rouvert["next_question"]["question_code"], "budget_annuel_max")

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
