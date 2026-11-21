# Test minimal Gemini

Test manuel séparé du questionnaire et du backend, avec Python 3.10 ou plus.
Le SDK recommandé par Google est `google-genai` ; `python-dotenv` sert à lire
uniquement la configuration locale, sans modifier les variables d'environnement.
Les versions utilisées sont dans `requirements-gemini.txt`.

Depuis la racine du dépôt, dans PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ai/chatbot/requirements-gemini.txt
.\.venv\Scripts\python.exe ai/chatbot/gemini_connection_check.py
```

Créer le venv seulement s'il n'existe pas déjà. Dans le `.env` racine ignoré
par Git, renseigner `GEMINI_API_KEY` localement. Ne jamais partager la clé.
Le script lit ce fichier sans l'écrire et sans afficher les secrets.

Chaque exécution lance au maximum une requête, sans nouvelle tentative
automatique, sans outils, sans historique et sans prompt système. Le seul
message envoyé est : « Réponds en français : Bonjour, connexion réussie. »
Le modèle est `gemini-3.5-flash-lite`. Une erreur 429 arrête le test ; le script
ne change pas de modèle, n'active aucune facturation et masque les erreurs brutes.
Ne pas relancer en boucle si le quota est indisponible.

La grille officielle consultée le 16 novembre 2026 indique des entrées et
sorties gratuites pour ce modèle en offre gratuite standard. Cela ne garantit
pas la disponibilité du quota pour une clé donnée. Le script ne peut pas
vérifier le statut de facturation du projet : utiliser une clé d'un projet en
offre gratuite ; un projet déjà payant suit sa propre tarification.

Sources officielles :

- [SDK Python Google Gen AI](https://googleapis.github.io/python-genai/)
- [Démarrage Gemini](https://ai.google.dev/gemini-api/docs/quickstart)
- [Tarification de Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite)
- [Capacités de Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)

Ce test ne connecte pas Gemini au questionnaire, au backend ou au RAG.

## Résultat du premier essai — 16 novembre 2026

Une seule requête réelle a été effectuée avec `gemini-2.5-flash-lite`.
L'API a renvoyé HTTP 404 : modèle indisponible pour cette requête ou ce projet.
Aucune réponse textuelle du modèle n'a été reçue. Ce résultat ne permet pas
de conclure à un quota gratuit épuisé. Aucun nouvel essai, aucun autre modèle
et aucune activation de facturation n'ont été effectués.

## Vérification des modèles et second essai — 16 novembre 2026

La même clé a été utilisée avec `client.models.list()` du SDK officiel,
sans génération à cette étape. L'API a renvoyé 28 modèles, dont 26 annoncent
`generateContent`. Cette capacité ne garantit ni une sortie textuelle ni
un quota gratuit disponible. Les deux modèles d'embeddings ont été exclus.

Parmi les modèles listés figurent `gemini-2.5-flash-lite`, malgré le 404 initial,
ainsi que `gemini-3.1-flash-lite` et `gemini-3.5-flash-lite`.
La liste seule ne permet donc pas de conclure qu'un appel fonctionnera.
La grille officielle indique une offre gratuite standard pour les entrées et
sorties des deux modèles Flash-Lite 3.1 et 3.5. En revanche, les modèles
également listés `gemini-4-argon` et `gemini-4-carbon` n'ont pas d'offre gratuite.

`gemini-3.5-flash-lite` a été retenu : présent dans la liste avec
`generateContent`, sortie texte confirmée par sa fiche officielle et gratuité
API standard confirmée séparément par la tarification. Le script utilise
désormais cet identifiant, sans repli automatique sur un autre modèle.

Une seule nouvelle requête de génération a été effectuée, avec le message
fictif initial et sans nouvelle tentative automatique. Une vraie réponse
textuelle a été reçue :

> Bonjour ! C'est bien noté. Comment puis-je vous aider aujourd'hui ?

La connexion fonctionne ; le modèle n'a pas repris exactement la phrase
« Bonjour, connexion réussie ». Ce test vérifie seulement la connexion,
pas le comportement du futur chatbot ou les prompts du module.
Le `.env` et les autres secrets n'ont pas été modifiés ni affichés.
Aucun réglage de facturation, questionnaire ou backend n'a été changé.
