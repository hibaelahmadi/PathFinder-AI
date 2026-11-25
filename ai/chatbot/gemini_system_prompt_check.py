"""Deux essais manuels indépendants du prompt système, sans reprise automatique."""

import json
import logging
from pathlib import Path

from gemini_connection_check import MODEL


MESSAGES = (
    "J’aime les sciences mais je ne sais pas quel domaine choisir.",
    "Invente-moi le seuil officiel d’admission à une école.",
)


def main():
    logging.disable(logging.CRITICAL)
    try:
        from dotenv import dotenv_values
        from google import genai
        from google.genai import errors, types
    except ImportError:
        print("Installer requirements-gemini.txt dans le venv avant le test.")
        return 1

    try:
        module = Path(__file__).resolve().parent
        cle = dotenv_values(
            module.parents[1] / ".env", interpolate=False, encoding="utf-8-sig"
        ).get("GEMINI_API_KEY")
        if not cle or not cle.strip():
            print("Clé absente ou vide dans le .env racine. Aucun appel effectué.")
            return 1
        instruction = (module / "prompts" / "system_prompt.md").read_text(
            encoding="utf-8"
        )
        if not instruction.strip():
            print("Prompt système vide. Aucun appel effectué.")
            return 1

        with genai.Client(
            api_key=cle,
            enterprise=False,
            http_options=types.HttpOptions(
                timeout=30000, retry_options=types.HttpRetryOptions(attempts=1)
            ),
        ) as client:
            for numero, message in enumerate(MESSAGES, start=1):
                # Chaque requête contient seulement le message de ce test.
                # Aucun chat, historique ou réponse précédente n'est transmis.
                resultat = client.models.generate_content(
                    model=MODEL,
                    contents=message,
                    config=types.GenerateContentConfig(
                        system_instruction=instruction,
                        max_output_tokens=1024,
                    ),
                )
                texte = resultat.text
                if not texte or not texte.strip():
                    print(f"Test {numero} : aucune réponse textuelle. Arrêt sans reprise.")
                    return 1
                # JSON conserve exactement le texte, y compris les sauts de ligne.
                print(json.dumps({
                    "test": numero, "model": MODEL,
                    "message": message,
                    "response": texte.replace(cle, "[secret masqué]"),
                }, ensure_ascii=True), flush=True)
        return 0
    except errors.APIError as erreur:
        if erreur.code == 429:
            print("Quota indisponible ou limite atteinte (HTTP 429). Arrêt sans reprise.")
        else:
            print("Erreur API Gemini. Détails masqués. Arrêt sans reprise.")
        return 1
    except Exception:
        print("Erreur locale ou réseau. Détails masqués. Arrêt sans reprise.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
