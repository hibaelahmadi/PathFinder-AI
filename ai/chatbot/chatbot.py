import json
from pathlib import Path
from saisie_notes import saisir_notes
from validation_profil import valider_budget_annuel, valider_type_etablissement
from questionnaire import (
    choisir_question_interets,
    QUESTIONS,
    creer_profil,
    corriger_reponse,
    prochaine_question,
    traiter_reponse,
)




def demander_mobilite():
    """Interprète une phrase seulement après accord explicite de l'élève."""
    choix = ("oui", "non", "je ne sais pas")
    while True:
        texte = input(QUESTIONS["mobilite"])
        valeur = texte.strip().lower()
        if valeur in choix:
            return valeur

        try:
            from mobilite_gemini import extraire_mobilite

            extraction = extraire_mobilite(texte)
        except Exception:
            # Ne jamais afficher les détails d'une erreur susceptible de contenir une clé.
            extraction = None

        if not extraction:
            print("Interprétation indisponible. Écris oui, non ou je ne sais pas.")
            continue
        if extraction["clarification_needed"]:
            print(extraction["clarification_question"])
            print("Tu peux répondre : oui, non ou je ne sais pas.")
            continue

        valeur = extraction["valeur"]
        if valeur not in choix:
            print("Interprétation indisponible. Écris oui, non ou je ne sais pas.")
            continue
        while True:
            accord = input(
                f"J’ai compris : {valeur}. Est-ce correct ? (oui / non) "
            ).strip().lower()
            if accord in ("oui", "non"):
                break
            print("Écris oui ou non.")
        if accord == "oui":
            return valeur
        print("D'accord, reprenons la réponse sur la mobilité.")


VALIDATIONS_TERMINAL = {
    "budget_annuel_max": valider_budget_annuel,
    "type_etablissement": valider_type_etablissement,
}


def demander_champ_valide(cle):
    """Redemande un champ du terminal jusqu'à une saisie valide ou vide."""
    while True:
        resultat = VALIDATIONS_TERMINAL[cle](input(QUESTIONS[cle]))
        if not resultat["errors"]:
            return resultat["value"]
        for erreur in resultat["errors"]:
            print(erreur)


def analyser_interets_terminal(texte, codes):
    """Aucun échec d'extraction ne doit bloquer le terminal."""
    try:
        from interets_gemini import extraire_interets
        resultat = extraire_interets(texte, codes)
        if not resultat["errors"]:
            return resultat
    except Exception:
        pass
    print("Catégories indisponibles ; tu peux continuer avec tes réponses libres.")
    return None


def recueillir_interets(reponses, texte, codes, *, correction=False):
    fonction = corriger_reponse if correction else traiter_reponse
    reponses = fonction(reponses, "interets", texte)["reponses"]
    reponses["interets_texte_original"] = texte
    reponses["categories_interets"] = None
    extraction = analyser_interets_terminal(texte, codes)
    besoin = extraction is not None and extraction["clarification_needed"]
    question = (extraction["clarification_question"] if besoin
                else choisir_question_interets(reponses.get("interets")))
    precision = input(question)
    fonction_precision = (corriger_reponse if "precision_interets" in reponses
                          else traiter_reponse)
    reponses = fonction_precision(reponses, "precision_interets", precision)["reponses"]
    reponses["precision_interets_texte_original"] = precision
    if besoin:
        # Une seule relance : si l'analyse combinée reste vague, continuer.
        extraction = analyser_interets_terminal(
            f"Réponse initiale : {texte}\nPrécision : {precision}", codes
        )
    if extraction is not None and not extraction["clarification_needed"]:
        reponses["categories_interets"] = extraction["codes"]
    return reponses


def actualiser_competences(reponses, texte, codes):
    reponses["competences_texte_original"] = texte
    reponses["categories_competences"] = None
    if not texte.strip():
        return
    try:
        from competences_gemini import extraire_competences
        resultat = extraire_competences(texte, codes)
        if not resultat["errors"] and not resultat["clarification_needed"]:
            reponses["categories_competences"] = resultat["codes"]
    except Exception:
        pass


def actualiser_objectif(reponses, texte, codes):
    reponses["objectif_texte_original"] = texte
    reponses["code_metier"] = None
    if not texte.strip():
        return
    try:
        from objectif_gemini import extraire_objectif
        resultat = extraire_objectif(texte, codes)
        if not resultat["errors"] and not resultat["clarification_needed"]:
            reponses["code_metier"] = resultat["code_metier"]
    except Exception:
        pass


def completer_questionnaire(reponses, codes_interets=None, codes_competences=None,
                           codes_metiers=None):
    """Pose dans le terminal les questions restant à traiter."""
    question = prochaine_question(reponses)
    while question is not None:
        if question["question_code"] == "interets" and codes_interets:
            reponses = recueillir_interets(
                reponses, input(question["question_text"]), codes_interets
            )
            question = prochaine_question(reponses)
            continue
        if question["question_code"] == "mobilite":
            reponse = demander_mobilite()
        else:
            reponse = input(question["question_text"])
        resultat = traiter_reponse(reponses, question["question_code"], reponse)

        for erreur in resultat["errors"]:
            print(erreur)

        reponses = resultat["reponses"]
        if question["question_code"] == "competences_declarees" and codes_competences and not resultat["errors"]:
            actualiser_competences(reponses, reponse, codes_competences)
        if question["question_code"] == "objectif" and codes_metiers and not resultat["errors"]:
            actualiser_objectif(reponses, reponse, codes_metiers)
        question = resultat["next_question"]

    for cle in VALIDATIONS_TERMINAL:
        if cle not in reponses:
            reponses[cle] = demander_champ_valide(cle)
    return reponses


def main(matieres=None, codes_interets=None, codes_competences=None, codes_metiers=None):
    """Lance le terminal ; sans liste, aucune question de notes n’est posée."""
    print("Bienvenue dans PathFinder AI !")
    print("Pour ce test, utilise des réponses fictives.\n")
    reponses = completer_questionnaire({}, codes_interets, codes_competences, codes_metiers)
    if matieres:
        reponses["notes"] = saisir_notes(matieres)

    # Associe chaque numéro au champ à modifier.
    champs = {
        "1": ("bac", "Série de bac"),
        "2": ("ville_souhaitee", "Ville souhaitée"),
        "3": ("interets", "Intérêts"),
        "4": ("precision_interets", "Précision des intérêts"),
        "5": ("mobilite", "Mobilité"),
        "6": ("autres_villes", "Autres villes"),
        "7": ("objectif", "Objectif"),
        "8": ("competences_declarees", "Compétences déclarées"),
        "9": ("budget_annuel_max", "Budget annuel maximal de scolarité (DH)"),
        "10": ("type_etablissement", "Type d'établissement"),
    }

    if matieres:
        champs["11"] = ("notes", "Notes par matière sur 20")

    while True:
        profil = creer_profil()
        profil.update(reponses)
        print("\n--- Profil à vérifier ---")

        for numero, (cle, titre) in champs.items():
            valeur = profil[cle]
            print(
                f"{numero}. {titre} :",
                valeur if valeur is not None else "Non renseigné",
            )

        if codes_interets:
            print("Catégories d'intérêts proposées :",
                  profil.get("categories_interets") or "Non renseigné")
        if codes_competences:
            print("Catégories de compétences déclarées proposées :",
                  profil.get("categories_competences") or "Non renseigné")
        if codes_metiers:
            print("Métier proposé (code) :", profil.get("code_metier") or "Non renseigné")

        confirmation = input(
            "\nCe résumé est-il correct ? (oui / non) "
        ).strip().lower()

        if confirmation == "oui":
            profil["confirme"] = True
            print("Ton profil est confirmé.")
            break

        if confirmation != "non":
            print("Écris oui ou non.")
            continue

        choix = input(
            f"Quel champ souhaites-tu corriger ? (numéro de 1 à {len(champs)}) "
        ).strip()

        if choix not in champs:
            print(f"Choisis un numéro entre 1 et {len(champs)}.")
            continue

        cle, titre = champs[choix]

        if cle == "notes":
            reponses["notes"] = saisir_notes(
                matieres, reponses.get("notes"), correction=True
            )
            continue

        if cle == "precision_interets":
            question = choisir_question_interets(reponses.get("interets"))
        else:
            question = QUESTIONS[cle]

        print(f"\nCorrection : {titre}")
        print("Appuie sur Entrée pour laisser ce champ vide.")
        if cle in VALIDATIONS_TERMINAL:
            reponses[cle] = demander_champ_valide(cle)
            continue
        reponse = demander_mobilite() if cle == "mobilite" else input(question)
        if cle == "interets" and codes_interets:
            reponses = recueillir_interets(
                reponses, reponse, codes_interets, correction=True
            )
            continue
        resultat = corriger_reponse(reponses, cle, reponse)

        for erreur in resultat["errors"]:
            print(erreur)

        reponses = resultat["reponses"]
        if not resultat["errors"]:
            if cle == "objectif" and codes_metiers:
                actualiser_objectif(reponses, reponse, codes_metiers)
            if cle == "competences_declarees" and codes_competences:
                actualiser_competences(reponses, reponse, codes_competences)
            if cle == "precision_interets" and codes_interets:
                reponses["precision_interets_texte_original"] = reponse
                reponses["categories_interets"] = None
                extraction = analyser_interets_terminal(
                    f"Réponse initiale : {reponses['interets_texte_original']}\nPrécision : {reponse}",
                    codes_interets,
                )
                if extraction is not None and not extraction["clarification_needed"]:
                    reponses["categories_interets"] = extraction["codes"]
            reponses = completer_questionnaire(reponses, codes_interets, codes_competences, codes_metiers)

    chemin = Path(__file__).resolve().parent / "profil_test.json"

    try:
        with chemin.open("w", encoding="utf-8") as fichier:
            json.dump(profil, fichier, ensure_ascii=False, indent=4)

        print(f"\nProfil sauvegardé dans : {chemin}")

    except OSError as erreur:
        print(f"\nImpossible de sauvegarder le profil : {erreur}")

    return {"profil": profil, "reponses": reponses}


if __name__ == "__main__":
    resultat_terminal = main()
    reponses = resultat_terminal["reponses"]
