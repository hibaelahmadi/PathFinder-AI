import json
from pathlib import Path
from questionnaire import choisir_question_interets
print("Bienvenue dans PathFinder AI !")
print("Pour ce test, utilise des réponses fictives.\n")

bac = input("Quelle est ta série de bac ? ")
ville = input("Dans quelle ville souhaites-tu étudier ? ")
interets = input("Quelles matières ou activités aimes-tu ? ")

question = choisir_question_interets(interets)
precision = input(question).strip() or None
# On accepte uniquement les réponses prévues.
while True:
    mobilite = input(
        "Acceptes-tu d'étudier dans une autre ville ? "
        "(oui / non / je ne sais pas) "
    ).strip().lower()

    if mobilite in ["oui", "non", "je ne sais pas"]:
        break

    print("Écris oui, non ou je ne sais pas.")

# La question suivante dépend de la mobilité.
if mobilite == "oui":
    villes_possibles = input(
        "Quelles autres villes envisages-tu ? "
        "Tu peux écrire « aucune préférence ». "
    )
elif mobilite == "non":
    villes_possibles = None
else:
    villes_possibles = None
    print("D'accord, ta mobilité reste à préciser.")
objectif = input(
    "Quel métier ou domaine aimerais-tu explorer ? "
    "Tu peux répondre « je ne sais pas ». "
).strip()

competences = input(
    "Dans quelles activités te sens-tu à l'aise ? "
    "Par exemple : analyser, créer, communiquer, aider, "
    "résoudre des problèmes. Tu peux passer avec Entrée. "
).strip()
profil = {
    "bac": bac,
    "ville_souhaitee": ville,
    "interets": interets,
    "precision_interets": precision,
    "mobilite": mobilite,
    "autres_villes": villes_possibles,
    "objectif": objectif if objectif else None,
    "competences_declarees": competences if competences else None
}
print("\n--- Résumé de ton profil ---")
print("Série de bac :", profil["bac"])
print("Ville souhaitée :", profil["ville_souhaitee"])
print("Intérêts :", profil["interets"])
print("Précision :", profil["precision_interets"])
print("Mobilité :", profil["mobilite"])
print("Autres villes :", profil["autres_villes"])
print("Objectif :", profil["objectif"] or "Non renseigné")
print(
    "Compétences déclarées :",
    profil["competences_declarees"] or "Non renseignées"
)
# Associe chaque numéro au champ à modifier.
champs = {
    "1": ("bac", "Série de bac"),
    "2": ("ville_souhaitee", "Ville souhaitée"),
    "3": ("interets", "Intérêts"),
    "4": ("precision_interets", "Précision des intérêts"),
    "5": ("mobilite", "Mobilité"),
    "6": ("autres_villes", "Autres villes"),
    "7": ("objectif", "Objectif"),
    "8": ("competences_declarees", "Compétences déclarées")
}

while True:
    print("\n--- Profil à vérifier ---")
    for numero, (cle, titre) in champs.items():
        valeur = profil[cle]
        print(
            f"{numero}. {titre} :",
            valeur if valeur is not None else "Non renseigné"
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
            reponse = input(
                "Acceptes-tu une autre ville ? "
                "(oui / non / je ne sais pas) "
            ).strip().lower()

            if reponse in ["oui", "non", "je ne sais pas"]:
                break
            print("Écris oui, non ou je ne sais pas.")

        profil["mobilite"] = reponse
        profil["autres_villes"] = None

        if reponse == "oui":
            profil["autres_villes"] = input(
                "Quelles autres villes envisages-tu ? "
                "Tu peux écrire « aucune préférence » : "
            ).strip() or None

    elif cle == "autres_villes" and profil["mobilite"] != "oui":
        print("Pour ajouter des villes, corrige d'abord la mobilité.")

    else:
        reponse = input(
            f"{titre} — nouvelle réponse "
            "(Entrée pour laisser vide) : "
        ).strip()

        profil[cle] = reponse or None

        # Une modification des intérêts déclenche une nouvelle précision.
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