from copy import deepcopy

if __package__:
    from .validation_profil import valider_budget_annuel, valider_type_etablissement, valider_note
else:
    from validation_profil import valider_budget_annuel, valider_type_etablissement, valider_note


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
    "notes": (
        "Quelles sont tes notes par matière sur 20 ? "
        "Cette réponse est facultative : appuie sur Entrée pour passer. "
        "0 est une vraie note et ne signifie pas une réponse vide. "
    ),
    "budget_annuel_max": (
        "Quel est ton budget annuel maximal en DH pour les frais de scolarité "
        "annuels uniquement, hors frais d'inscription, logement et transport ? "
        "Cette réponse est facultative : appuie sur Entrée pour passer. "
        "0 est un vrai budget et ne signifie pas une réponse vide. "
    ),
    "type_etablissement": (
        "Quel type d'établissement préfères-tu : public, privé ou sans préférence ? "
        "Cette réponse est facultative : appuie sur Entrée pour passer. "
    ),
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
        "notes": None,
        "budget_annuel_max": None,
        "type_etablissement": None,
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



def _enrichir_profil(profil, answers, codes_interets, codes_competences, codes_metiers):
    """Enrichit un instantané ; chaque extraction peut échouer indépendamment."""
    from importlib import import_module

    originaux = {entree["question_code"]: entree["answer_text"] for entree in answers}
    interets = originaux.get("interets", "")
    precision = originaux.get("precision_interets", "")
    if precision.strip():
        interets = f"Réponse initiale : {interets}\nPrécision : {precision}"
    extractions = [
        ("categories_interets", "interets_gemini", "extraire_interets", interets, codes_interets, "codes"),
        ("categories_competences", "competences_gemini", "extraire_competences",
         originaux.get("competences_declarees", ""), codes_competences, "codes"),
        ("code_metier", "objectif_gemini", "extraire_objectif",
         originaux.get("objectif", ""), codes_metiers, "code_metier"),
    ]
    for champ, module, fonction, texte, codes, cle in extractions:
        profil[champ] = None
        if not texte.strip() or not codes:
            continue
        try:
            module = import_module(f".{module}", __package__) if __package__ else import_module(module)
            retour = getattr(module, fonction)(texte, deepcopy(codes))
            if not retour["errors"] and not retour["clarification_needed"]:
                profil[champ] = retour[cle]
        except Exception:
            # Les détails d'erreur peuvent contenir des secrets ; ne pas les exposer.
            pass


def traiter_questionnaire(etat, action, reponse=None, *, inclure_budget_type=False, matieres=None,
                         enrichir_profil=False, codes_interets=None,
                         codes_competences=None, codes_metiers=None):
    """Adapte synchroniquement le questionnaire à un état échangeable en JSON.

    answers est un dictionnaire indexé par question_code.
    reponse contient question_code, answer_text et les métadonnées facultatives.
    Les métadonnées des questions et valeurs structurées sont recalculées.
    Aucun objet reçu n'est modifié et aucune persistance n'est effectuée.
    inclure_budget_type=True ajoute budget et type après les compétences.
    matieres fournit les codes ordonnés des questions finales note:<code>.
    La même liste doit être fournie à chaque appel de la session.
    enrichir_profil active les extractions seulement lors d'un confirm valide.
    Le mode est fourni par l'appelant à chaque appel, sans modifier le contrat
    d'état. Une ancienne session completed reste confirmée jusqu'à reopen.
    """
    initial = deepcopy(etat)
    valeurs = {}
    entrees = []
    errors = []
    status = "in_progress"
    notes_questions = {}
    if matieres is not None:
        if (not isinstance(matieres, list)
                or any(not isinstance(m, str) or not m.strip() for m in matieres)
                or len(matieres) != len(set(matieres))):
            errors.append("matieres doit être une liste ordonnée de codes textuels uniques non vides.")
        else:
            notes_questions = {f"note:{matiere}": matiere for matiere in matieres}
    codes = set(QUESTIONS) | {"precision_interets"} | set(notes_questions)
    validations = {
        "budget_annuel_max": valider_budget_annuel,
        "type_etablissement": valider_type_etablissement,
    }

    def valider(code, texte):
        if code in notes_questions:
            retour = valider_note(texte)
            return retour["value"], retour["errors"]
        if code in validations:
            retour = validations[code](texte)
            return retour["value"], retour["errors"]
        return _valider_reponse(code, texte)

    def question_suivante():
        question = prochaine_question(valeurs)
        if question is not None:
            return question
        ancien_budget = status == "completed" and not any(c in valeurs for c in validations)
        if inclure_budget_type and not ancien_budget:
            for code in validations:
                if code not in valeurs:
                    return {"question_code": code, "question_text": QUESTIONS[code]}
        anciennes_notes = status == "completed" and not any(c in valeurs for c in notes_questions)
        if not anciennes_notes:
            for code, matiere in notes_questions.items():
                if code not in valeurs:
                    return {"question_code": code, "question_text": texte_note(matiere)}
        return None

    def texte_note(matiere):
        return (f"Note pour {matiere} sur 20 ? Entrée permet de passer "
                "ou d'effacer la note en correction ; 0 est une vraie note. ")

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
                valeur, erreurs = valider(code, entree.get("answer_text"))
                errors.extend(erreurs)
                if not erreurs:
                    valeurs[code] = valeur
                    entrees.append({"question_code": code,
                                    "answer_text": entree["answer_text"]})
            if "autres_villes" in valeurs and valeurs.get("mobilite") != "oui":
                errors.append("Les autres villes nécessitent une mobilité acceptée.")
        if status == "completed" and question_suivante() is not None:
            errors.append("Un entretien completed doit avoir traité toutes les questions.")

    def texte_question(code):
        if code in notes_questions:
            return texte_note(notes_questions[code])
        if code == "precision_interets":
            return choisir_question_interets(valeurs.get("interets"))
        return QUESTIONS[code]

    def canoniser(entree):
        code = entree["question_code"]
        return {"question_code": code, "question_text": texte_question(code),
                "answer_text": entree["answer_text"], "answer_value": valeurs[code]}

    def resultat(erreurs, sauvegardes=None, suppressions=None):
        suivante = question_suivante()
        confirme = status == "completed" and suivante is None and not errors
        profil = creer_profil()
        profil.update({code: valeur for code, valeur in valeurs.items() if code not in notes_questions})
        profil["notes"] = {
            matiere: valeurs[code] for code, matiere in notes_questions.items()
            if code in valeurs and valeurs[code] is not None
        } or None
        profil["confirme"] = confirme
        if enrichir_profil and action == "confirm" and confirme and not erreurs:
            _enrichir_profil(profil, entrees, codes_interets, codes_competences, codes_metiers)
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
        if question_suivante() is not None:
            return resultat(["Toutes les questions applicables doivent être traitées."])
        status = "completed"
        return resultat([])
    if not isinstance(reponse, dict):
        return resultat(["La réponse doit contenir question_code et answer_text."])
    code = reponse.get("question_code")
    if not isinstance(code, str):
        return resultat(["question_code doit être une chaîne de caractères."])
    if code in validations or code in notes_questions:
        erreurs = []
        if code in validations and not inclure_budget_type:
            erreurs.append("Le mode budget et type d'établissement n'est pas activé.")
        elif action == "answer":
            question = question_suivante()
            if question is None or question["question_code"] != code:
                erreurs.append("Le code ne correspond pas à la question attendue.")
        elif code not in valeurs:
            erreurs.append("Cette question n'a pas encore été traitée.")
        valeur, erreurs_validation = valider(code, reponse.get("answer_text"))
        erreurs.extend(erreurs_validation)
        traitement = {"reponses": {**valeurs, code: valeur}, "errors": erreurs}
    else:
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
