# Questionnaire PathFinder AI

Prototype en terminal du questionnaire de collecte du profil étudiant.

## Lancement

Depuis la racine du dépôt :

```bat
python ai\chatbot\chatbot.py
```

Python est nécessaire. Aucune bibliothèque externe n'est requise.

## Fonctionnalités actuelles

- Collecte du bac, de la ville souhaitée, des intérêts, de la mobilité,
  de l'objectif et des compétences déclarées.
- Questions de précision selon les mots-clés informatique ou biologie.
- Question sur les autres villes si la mobilité est acceptée.
- Affichage, correction et confirmation du profil.
- Sauvegarde locale dans profil_test.json après confirmation.
  Chaque lancement confirmé remplace le fichier précédent.

## Limites actuelles

- Aucun LLM ni module RAG connecté.
- Compréhension des intérêts limitée à des mots-clés.
- Validation des réponses encore partielle.
- Aucun scoring ni recommandation de formation.
- Format du profil à harmoniser avec les personnes 2 et 5.

Utiliser des données fictives pour les tests.
Le fichier profil_test.json est exclu de Git.