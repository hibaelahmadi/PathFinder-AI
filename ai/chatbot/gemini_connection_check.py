"""Test manuel isolé : une seule requête Gemini, sans nouvelle tentative."""

import logging
from pathlib import Path


MODEL = "gemini-3.5-flash-lite"
PROMPT = "Réponds en français : Bonjour, connexion réussie."


def main():
    # Aucune erreur brute ni journal HTTP ne doit révéler des identifiants.
    logging.disable(logging.CRITICAL)
    try:
        from dotenv import dotenv_values
        from google import genai
        from google.genai import errors, types
    except ImportError:
        print("Dépendances manquantes : installer requirements-gemini.txt dans le venv.")
        return 1

    try:
        chemin = Path(__file__).resolve().parents[2] / ".env"
        # Lecture seule, sans interpolation ni modification de l'environnement.
        cle = dotenv_values(chemin, interpolate=False, encoding="utf-8-sig").get(
            "GEMINI_API_KEY"
        )
        if not cle or not cle.strip():
            print("GEMINI_API_KEY absente ou vide dans le .env racine. Aucun appel effectué.")
            return 1
        with genai.Client(
            api_key=cle,
            enterprise=False,
            http_options=types.HttpOptions(
                timeout=30000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        ) as client:
            resultat = client.models.generate_content(
                model=MODEL,
                contents=PROMPT,
                config=types.GenerateContentConfig(max_output_tokens=64),
            )
        texte = resultat.text
        if not texte or not texte.strip():
            print(f"Modèle : {MODEL}. Appel terminé sans réponse textuelle. Aucun nouvel essai.")
            return 1
        print(f"Modèle : {MODEL}")
        print("Réponse reçue :", texte.replace(cle, "[secret masqué]").strip())
        return 0
    except errors.APIError as erreur:
        code = erreur.code
        if code == 429:
            message = "Quota indisponible ou limite atteinte (HTTP 429). Arrêt sans nouvel essai."
        elif code in (401, 403):
            message = "Authentification ou accès refusé. Vérifier la clé et les droits du projet."
        elif code == 404:
            message = "Modèle indisponible pour ce projet. Aucun autre modèle essayé."
        elif code == 400:
            message = "Requête refusée : vérifier la configuration du projet et de la clé."
        else:
            message = "Erreur du service Gemini. Arrêt sans nouvel essai."
        print(f"Modèle : {MODEL}. {message}")
        return 1
    except Exception:
        print("Test interrompu : erreur locale ou réseau. Détails masqués, aucun nouvel essai.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
