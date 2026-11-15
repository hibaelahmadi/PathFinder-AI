import json
from pathlib import Path
from questionnaire import (
    choisir_question_interets,
    QUESTIONS,
    creer_profil,
    prochaine_question,
    traiter_reponse,
)


print("Bienvenue dans PathFinder AI !")
print("Pour ce test, utilise des réponses fictives.\n")

# Un champ absent reste à demander ; une réponse vide est déjà traitée.
reponses = {}

question = prochaine_question(reponses)
while question is not None:
    reponse = input(question["question_text"])
    resultat = traiter_reponse(reponses, question["question_code"], reponse)

    for erreur in resultat["errors"]:
        print(erreur)

    reponses = resultat["reponses"]
    question = resultat["next_question"]

profil = creer_profil()
profil.update(reponses)

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

    # Modifier la mobilité implique de revoir les autres villes.
    if cle == "mobilite":
        while True:
            reponse = input(QUESTIONS["mobilite"]).strip().lower()

            if reponse in ["oui", "non", "je ne sais pas"]:
                break

            print("Écris oui, non ou je ne sais pas.")

        profil["mobilite"] = reponse
        profil["autres_villes"] = None

        if reponse == "oui":
            profil["autres_villes"] = (
                input(QUESTIONS["autres_villes"]).strip() or None
            )

    elif cle == "autres_villes" and profil["mobilite"] != "oui":
        print("Pour ajouter des villes, corrige d'abord la mobilité.")

    else:
        # La précision des intérêts dépend des intérêts actuels.
        if cle == "precision_interets":
            question = choisir_question_interets(profil["interets"])
        else:
            question = QUESTIONS[cle]

        print(f"\nCorrection : {titre}")
        print("Appuie sur Entrée pour laisser ce champ vide.")
        profil[cle] = input(question).strip() or None

        # Modifier les intérêts remplace aussi leur ancienne précision.
        if cle == "interets":
            question = choisir_question_interets(profil["interets"])
            profil["precision_interets"] = input(question).strip() or None

chemin = Path(__file__).resolve().parent / "profil_test.json"

try:
    with chemin.open("w", encoding="utf-8") as fichier:
        json.dump(profil, fichier, ensure_ascii=False, indent=4)

    print(f"\nProfil sauvegardé dans : {chemin}")

except OSError as erreur:
    print(f"\nImpossible de sauvegarder le profil : {erreur}")