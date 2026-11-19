import json
from pathlib import Path
from questionnaire import (
    choisir_question_interets,
    QUESTIONS,
    creer_profil,
    corriger_reponse,
    prochaine_question,
    traiter_reponse,
)


print("Bienvenue dans PathFinder AI !")
print("Pour ce test, utilise des réponses fictives.\n")


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


def completer_questionnaire(reponses):
    """Pose dans le terminal les questions restant à traiter."""
    question = prochaine_question(reponses)
    while question is not None:
        if question["question_code"] == "mobilite":
            reponse = demander_mobilite()
        else:
            reponse = input(question["question_text"])
        resultat = traiter_reponse(reponses, question["question_code"], reponse)

        for erreur in resultat["errors"]:
            print(erreur)

        reponses = resultat["reponses"]
        question = resultat["next_question"]

    return reponses


reponses = completer_questionnaire({})

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
}

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
        "Quel champ souhaites-tu corriger ? (numéro de 1 à 8) "
    ).strip()

    if choix not in champs:
        print("Choisis un numéro entre 1 et 8.")
        continue

    cle, titre = champs[choix]

    if cle == "precision_interets":
        question = choisir_question_interets(reponses.get("interets"))
    else:
        question = QUESTIONS[cle]

    print(f"\nCorrection : {titre}")
    print("Appuie sur Entrée pour laisser ce champ vide.")
    reponse = demander_mobilite() if cle == "mobilite" else input(question)
    resultat = corriger_reponse(reponses, cle, reponse)

    for erreur in resultat["errors"]:
        print(erreur)

    reponses = resultat["reponses"]
    if not resultat["errors"]:
        reponses = completer_questionnaire(reponses)

chemin = Path(__file__).resolve().parent / "profil_test.json"

try:
    with chemin.open("w", encoding="utf-8") as fichier:
        json.dump(profil, fichier, ensure_ascii=False, indent=4)

    print(f"\nProfil sauvegardé dans : {chemin}")

except OSError as erreur:
    print(f"\nImpossible de sauvegarder le profil : {erreur}")
