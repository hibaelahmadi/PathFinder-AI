from copy import deepcopy


def choisir_question_interets(interets):
    """Choisit une question de précision selon les intérêts."""
    texte = (interets or "").strip().lower()

    if "informatique" in texte:
        return (
            "Qu'est-ce qui t'attire en informatique : "
            "programmation, réseaux, données ou autre ? "
        )

    if "biologie" in texte:
        return (
            "Qu'est-ce qui t'attire en biologie : "
            "santé, recherche, environnement ou autre ? "
        )

    return (
        "Peux-tu donner un exemple d'activité que tu aimes ? "
        "Tu peux passer avec Entrée. "
    )


QUESTIONS = {
    "bac": "Quelle est ta série de bac ? ",
    "ville_souhaitee": "Dans quelle ville souhaites-tu étudier ? ",
    "interets": "Quelles matières ou activités aimes-tu ? ",
    "mobilite": (
        "Acceptes-tu d'étudier dans une autre ville ? "
        "(oui / non / je ne sais pas) "
    ),
    "autres_villes": (
        "Quelles autres villes envisages-tu ? "
        "Tu peux écrire « aucune préférence ». "
    ),
    "objectif": (
        "Quel métier ou domaine aimerais-tu explorer ? "
        "Tu peux répondre « je ne sais pas ». "
    ),
    "competences_declarees": (
        "Dans quelles activités te sens-tu à l'aise ? "
        "Par exemple : analyser, créer, communiquer, aider, "
        "résoudre des problèmes. Tu peux passer avec Entrée. "
    ),
}


def creer_profil():
    """Prépare un profil vide pour un nouvel entretien."""
    return {
        "bac": None,
        "ville_souhaitee": None,
        "interets": None,
        "precision_interets": None,
        "mobilite": None,
        "autres_villes": None,
        "objectif": None,
        "competences_declarees": None,
        "confirme": False,
    }
def prochaine_question(reponses):
    """Renvoie la prochaine question, ou None si le résumé est prêt."""
    ordre = [
        "bac",
        "ville_souhaitee",
        "interets",
        "precision_interets",
        "mobilite",
        "autres_villes",
        "objectif",
        "competences_declarees",
    ]

    for code in ordre:
        # On demande les autres villes seulement si la mobilité est acceptée.
        if code == "autres_villes":
            if reponses.get("mobilite") != "oui":
                continue

        # Un champ présent a déjà été traité, même si sa réponse est vide.
        if code in reponses:
            continue

        if code == "precision_interets":
            texte = choisir_question_interets(reponses.get("interets"))
        else:
            texte = QUESTIONS[code]

        return {
            "question_code": code,
            "question_text": texte,
        }

    return None


def _valider_reponse(question_code, answer_text):
    """Normalise une réponse et renvoie sa valeur et les erreurs éventuelles."""
    if not isinstance(answer_text, str):
        return None, ["La réponse doit être une chaîne de caractères."]

    valeur = answer_text.strip()
    if question_code == "mobilite":
        valeur = valeur.lower()
        if valeur not in ("oui", "non", "je ne sais pas"):
            return None, ["Écris oui, non ou je ne sais pas."]
    else:
        valeur = valeur or None
    return valeur, []


def traiter_reponse(reponses, question_code, answer_text):
    """Valide la réponse attendue et renvoie un nouvel état du questionnaire."""
    actualisees = reponses.copy()
    question = prochaine_question(reponses)
    errors = []

    if question is None:
        errors.append("Toutes les questions ont déjà été traitées.")
    elif question_code != question["question_code"]:
        errors.append("Le code ne correspond pas à la question attendue.")

    valeur, erreurs_validation = _valider_reponse(question_code, answer_text)
    errors.extend(erreurs_validation)

    if not errors:
        actualisees[question_code] = valeur

    suivante = prochaine_question(actualisees)
    return {
        "reponses": actualisees,
        "next_question": suivante,
        "ready_for_confirmation": suivante is None,
        "errors": errors,
    }


def corriger_reponse(reponses, question_code, answer_text):
    """Corrige une réponse traitée et invalide ses dépendances si elle change."""
    actualisees = reponses.copy()
    errors = []
    supprimees = []

    if question_code not in QUESTIONS and question_code != "precision_interets":
        errors.append("Le code ne correspond pas à une question du questionnaire.")
    elif question_code not in reponses:
        errors.append("Cette question n'a pas encore été traitée.")

    if question_code == "autres_villes" and reponses.get("mobilite") != "oui":
        errors.append("Les autres villes nécessitent une mobilité acceptée.")

    valeur, erreurs_validation = _valider_reponse(question_code, answer_text)
    errors.extend(erreurs_validation)

    if not errors:
        actualisees[question_code] = valeur
        if valeur != reponses[question_code]:
            dependances = {
                "interets": "precision_interets",
                "mobilite": "autres_villes",
            }
            dependante = dependances.get(question_code)
            if dependante in actualisees:
                del actualisees[dependante]
                supprimees.append(dependante)

    suivante = prochaine_question(actualisees)
    return {
        "reponses": actualisees,
        "next_question": suivante,
        "ready_for_confirmation": suivante is None,
        "errors": errors,
        "answer_codes_to_delete": supprimees,
    }



def traiter_questionnaire(etat, action, reponse=None):
    """Adapte synchroniquement le questionnaire à un état échangeable en JSON.

    answers est un dictionnaire indexé par question_code.
    reponse contient question_code, answer_text et les métadonnées facultatives.
    Les métadonnées des questions et valeurs structurées sont recalculées.
    Aucun objet reçu n'est modifié et aucune persistance n'est effectuée.
    """
    initial = deepcopy(etat)
    valeurs = {}
    entrees = []
    errors = []
    status = "in_progress"
    codes = set(QUESTIONS) | {"precision_interets"}

    if etat is None:
        if action != "start":
            errors.append("Un entretien doit être démarré avec start.")
    elif not isinstance(etat, dict):
        errors.append("L'état doit être un dictionnaire ou None pour start.")
    else:
        status = etat.get("status")
        if status not in ("in_progress", "completed"):
            errors.append("Le statut doit être in_progress ou completed.")
        answers = etat.get("answers")
        if not isinstance(answers, dict):
            errors.append("answers doit être un dictionnaire indexé par question_code.")
        else:
            for cle, entree in answers.items():
                if not isinstance(entree, dict):
                    errors.append("Chaque réponse doit être un dictionnaire.")
                    continue
                code = entree.get("question_code")
                if not isinstance(code, str) or code not in codes:
                    errors.append("Code de question inconnu dans answers.")
                    continue
                if cle != code:
                    errors.append("La clé de answers doit correspondre à question_code.")
                    continue
                valeur, erreurs = _valider_reponse(code, entree.get("answer_text"))
                errors.extend(erreurs)
                if not erreurs:
                    valeurs[code] = valeur
                    entrees.append({"question_code": code,
                                    "answer_text": entree["answer_text"]})
            if "autres_villes" in valeurs and valeurs.get("mobilite") != "oui":
                errors.append("Les autres villes nécessitent une mobilité acceptée.")
        if status == "completed" and prochaine_question(valeurs) is not None:
            errors.append("Un entretien completed doit avoir traité toutes les questions.")

    def texte_question(code):
        if code == "precision_interets":
            return choisir_question_interets(valeurs.get("interets"))
        return QUESTIONS[code]

    def canoniser(entree):
        code = entree["question_code"]
        return {"question_code": code, "question_text": texte_question(code),
                "answer_text": entree["answer_text"], "answer_value": valeurs[code]}

    def resultat(erreurs, sauvegardes=None, suppressions=None):
        suivante = prochaine_question(valeurs)
        confirme = status == "completed" and suivante is None and not errors
        profil = creer_profil()
        profil.update(valeurs)
        profil["confirme"] = confirme
        nouvel_etat = initial if erreurs else {
            "status": status,
            "expected_question_code": suivante["question_code"] if suivante else None,
            "answers": {entree["question_code"]: canoniser(entree) for entree in entrees},
        }
        return deepcopy({
            "etat": nouvel_etat, "next_question": suivante,
            "answers_to_save": [] if erreurs else (sauvegardes or []),
            "answer_codes_to_delete": [] if erreurs else (suppressions or []),
            "profile": profil, "profile_confirmed": confirme,
            "errors": erreurs,
        })

    if errors:
        return resultat(errors)
    if action not in ("start", "answer", "correct", "confirm", "reopen"):
        return resultat(["Action inconnue."])
    if action not in ("answer", "correct") and reponse is not None:
        return resultat(["Cette action n'accepte pas de réponse."])
    if action == "start":
        if entrees or status == "completed":
            return resultat(["Un entretien existant ne peut pas être réinitialisé."])
        return resultat([])
    if action == "reopen":
        if status != "completed":
            return resultat(["Seul un entretien completed peut être rouvert."])
        status = "in_progress"
        return resultat([])
    if status == "completed":
        return resultat(["Rouvre l'entretien avant de répondre ou de le corriger."])
    if action == "confirm":
        if prochaine_question(valeurs) is not None:
            return resultat(["Toutes les questions applicables doivent être traitées."])
        status = "completed"
        return resultat([])
    if not isinstance(reponse, dict):
        return resultat(["La réponse doit contenir question_code et answer_text."])
    code = reponse.get("question_code")
    if not isinstance(code, str):
        return resultat(["question_code doit être une chaîne de caractères."])
    fonction = traiter_reponse if action == "answer" else corriger_reponse
    traitement = fonction(valeurs, code, reponse.get("answer_text"))
    if traitement["errors"]:
        return resultat(traitement["errors"])
    valeurs = traitement["reponses"]
    supprimees = traitement.get("answer_codes_to_delete", [])
    entrees = [entree for entree in entrees
               if entree["question_code"] not in supprimees + [code]]
    entree = {"question_code": code, "answer_text": reponse["answer_text"]}
    entrees.append(entree)
    return resultat([], [canoniser(entree)], supprimees)
