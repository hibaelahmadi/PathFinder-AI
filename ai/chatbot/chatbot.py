import json
from pathlib import Path
from questionnaire import choisir_question_interets, QUESTIONS, creer_profil


print("Bienvenue dans PathFinder AI !")
print("Pour ce test, utilise des réponses fictives.\n")

bac = input(QUESTIONS["bac"]).strip() or None
ville = input(QUESTIONS["ville_souhaitee"]).strip() or None
interets = input(QUESTIONS["interets"]).strip() or None

question = choisir_question_interets(interets)
precision = input(question).strip() or None

# On accepte uniquement les réponses prévues.
while True:
    mobilite = input(QUESTIONS["mobilite"]).strip().lower()

    if mobilite in ["oui", "non", "je ne sais pas"]:
        break

    print("Écris oui, non ou je ne sais pas.")

# La question suivante dépend de la mobilité.
villes_possibles = None

if mobilite == "oui":
    villes_possibles = input(QUESTIONS["autres_villes"]).strip() or None
elif mobilite == "je ne sais pas":
    print("D'accord, ta mobilité reste à préciser.")

objectif = input(QUESTIONS["objectif"]).strip() or None
competences = input(QUESTIONS["competences_declarees"]).strip() or None

profil = creer_profil()

profil.update({
    "bac": bac,
    "ville_souhaitee": ville,
    "interets": interets,
    "precision_interets": precision,
    "mobilite": mobilite,
    "autres_villes": villes_possibles,
    "objectif": objectif,
    "competences_declarees": competences,
})

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