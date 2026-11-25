"""Préparation de la saisie terminal ; matières fournies par l'appelant."""

if __package__:
    from .validation_profil import valider_note
else:
    from validation_profil import valider_note


def saisir_notes(matieres, notes_existantes=None, *, correction=False):
    """Demande une note par code de matière fourni, sans liste prédéfinie.

    matieres est une liste de codes textuels distincts et non vides.
    Renvoie un dictionnaire code -> nombre, ou None si aucune note n'est saisie.
    Entrée ignore une matière ; en correction elle conserve sa note existante.
    La commande effacer supprime explicitement une note en correction.
    Ne modifie ni la liste reçue ni un profil et n'effectue aucune sauvegarde.
    """
    if not isinstance(matieres, list) or any(
        not isinstance(code, str) or not code.strip() for code in matieres
    ):
        raise ValueError("Fournir une liste de codes de matières non vides.")
    if len(set(matieres)) != len(matieres):
        raise ValueError("Les codes des matières doivent être distincts.")

    notes = dict(notes_existantes or {}) if correction else {}
    if correction:
        print("Notes : Entrée conserve la note ; écris effacer pour la supprimer.")
    for code in matieres:
        while True:
            consigne = "Entrée pour conserver ; effacer pour supprimer" if correction else "Entrée pour passer"
            actuelle = f" [actuelle : {notes[code]}]" if code in notes else ""
            texte = input(f"Note pour {code}{actuelle} sur 20 (0 est une note ; {consigne}) : ")
            if correction and not texte.strip():
                break
            if correction and texte.strip().lower() == "effacer":
                notes.pop(code, None)
                break
            resultat = valider_note(texte)
            if resultat["errors"]:
                for erreur in resultat["errors"]:
                    print(erreur)
                continue
            if resultat["value"] is not None:
                notes[code] = resultat["value"]
            break
    return notes or None
