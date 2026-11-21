# Extraction expérimentale de la mobilité

Module isolé du questionnaire, du contrat P2 et du backend. Aucune écriture
de profil, aucune confirmation et aucune sauvegarde.

```python
from ai.chatbot.mobilite_gemini import extraire_mobilite

resultat = extraire_mobilite("Ça dépend du logement.")
```

Appel synchrone avec `gemini-3.5-flash-lite`, les dépendances de
`requirements-gemini.txt` dans `.venv` et la clé lue dans le `.env` racine.
Un appel au maximum par entrée, sans historique ni nouvelle tentative.
Une entrée vide ou non textuelle ne déclenche aucun appel.

Le résultat comporte exactement :

- `valeur` : `oui`, `non`, `je ne sais pas` ou `null` ;
- `clarification_needed` : booléen strict ;
- `clarification_question` : question non vide si clarification, sinon `null`.

Une clarification impose une valeur `null`. Sans clarification, une des trois
valeurs textuelles est requise. Le schéma JSON est transmis à Gemini via
`response_mime_type` et `response_json_schema`, puis les clés, types, valeurs
et règles de cohérence sont validés en Python. Les clés supplémentaires ou
dupliquées et les JSON invalides sont refusés.

Une erreur API, locale ou de validation renvoie une clarification de secours :

```json
{
  "valeur": null,
  "clarification_needed": true,
  "clarification_question": "Je ne peux pas interpréter cette réponse pour le moment. Peux-tu préciser ta mobilité ?"
}
```

Ce résultat ne constitue pas une décision de l'élève. Les erreurs brutes ne sont
ni affichées ni journalisées. Le module désactive temporairement les logs pendant
l'appel et restaure ensuite leur niveau. Cette protection globale est destinée
à l'essai isolé ; elle devra être revue avant une intégration concurrente.

Le prompt exige une clarification pour les conditions non résolues. Une garde
Python conservatrice repère aussi certains mots (`si`, `dépend`, `condition`,
`logement`, etc.) et impose alors une clarification sans décision. Cette garde
peut demander une clarification inutile et ne couvre pas toutes les formulations.
La validation structurelle ne garantit pas l'interprétation sémantique.

## Vérifications du 16 novembre 2026

Les 29 tests du module chatbot passent, dont 6 nouveaux tests hors ligne
utilisant des sorties simulées. Ils ne nécessitent ni clé ni dépendance Gemini.

```powershell
python -B -m unittest discover -s ai/chatbot -p 'test*.py' -v
```

Trois appels réels, sans erreur et sans reprise, ont donné :

| Entrée fictive | Valeur | Clarification |
| --- | --- | --- |
| Oui, je peux déménager pour mes études. | `oui` | Non |
| Je veux rester uniquement dans ma ville. | `non` | Non |
| Ça dépend du logement. | `null` | Oui : « Ta mobilité dépend d'une condition. Peux-tu préciser ce qui reste à décider ? » |

La troisième question est celle imposée par la garde Python après validation
de la sortie structurée ; ces résultats sont ceux du module complet.
Ces essais ne prouvent pas une fiabilité générale. Aucun réglage de facturation
n'a été modifié et aucun secret n'a été affiché.

Sources officielles consultées :

- [Sorties structurées Gemini](https://ai.google.dev/gemini-api/docs/structured-output)
- [SDK Google Gen AI : schéma JSON et génération](https://googleapis.github.io/python-genai/)
