# Questionnaire PathFinder AI

Prototype en terminal du questionnaire de collecte du profil étudiant.

## Lancement

Depuis la racine du dépôt :

```bat
python ai\chatbot\chatbot.py
```

Python est nécessaire. Aucune bibliothèque externe n'est requise.

## Tests

Depuis la racine du dépôt :

```powershell
python -B -m unittest discover -s ai/chatbot -p 'test*.py' -v
```

Les 15 tests utilisent des réponses fictives et ne sauvegardent aucun profil.
La commande de lancement a également été vérifiée avec une copie temporaire
du chatbot, sans remplacer le profil local.

## Fonctionnalités actuelles

- Collecte du bac, de la ville souhaitée, des intérêts, de la mobilité,
  de l'objectif et des compétences déclarées.
- Questions de précision selon les mots-clés informatique ou biologie.
- Question sur les autres villes si la mobilité est acceptée.
- Affichage, correction et confirmation du profil.
- Sauvegarde locale dans profil_test.json après confirmation.
  Chaque lancement confirmé remplace le fichier précédent.

## Fonctions publiques de questionnaire.py

Ces fonctions n'utilisent ni `input`, ni `print`, ni sauvegarde. Le terminal
et la confirmation du profil sont gérés par `chatbot.py`.

| Fonction | Paramètres | Résultat |
| --- | --- | --- |
| `choisir_question_interets(interets)` | Texte des intérêts, ou `None`. | Texte de la question de précision : informatique, biologie ou question générique. La recherche des mots-clés ignore les majuscules. |
| `creer_profil()` | Aucun. | Nouveau dictionnaire contenant les huit champs du profil à `None` et `confirme` à `False`. |
| `prochaine_question(reponses)` | Dictionnaire des réponses déjà traitées. | Dictionnaire avec `question_code` et `question_text`, ou `None` si toutes les questions applicables sont traitées. |
| `traiter_reponse(reponses, question_code, answer_text)` | Réponses actuelles, code de la question attendue et réponse textuelle. | État actualisé décrit ci-dessous. Refuse une réponse à une autre question ou après la fin du questionnaire. |
| `corriger_reponse(reponses, question_code, answer_text)` | Réponses actuelles, code d'une question déjà traitée et nouvelle réponse textuelle. | Même état, avec en plus `answer_codes_to_delete`. Refuse un code inconnu, une question non traitée ou `autres_villes` si la mobilité n'est pas `oui`. |

L'ordre des questions est : `bac`, `ville_souhaitee`, `interets`,
`precision_interets`, `mobilite`, `autres_villes`, `objectif`,
`competences_declarees`. La question `autres_villes` n'est applicable que
si `mobilite` vaut `oui`.

### Validation et résultat d'une réponse

`traiter_reponse` et `corriger_reponse` partagent les mêmes règles :
`answer_text` doit être une chaîne, les espaces au début et à la fin sont
retirés, et une réponse vide devient `None` sauf pour la mobilité. Pour
`mobilite`, seules `oui`, `non` et `je ne sais pas` sont acceptées, sans
tenir compte des majuscules ; une réponse vide est refusée.

Les deux fonctions travaillent sur une copie et préservent le dictionnaire
reçu. Elles renvoient :

- `reponses` : copie actualisée, ou copie des réponses initiales en cas d'erreur ;
- `next_question` : prochaine question applicable, ou `None` ;
- `ready_for_confirmation` : `True` uniquement si toutes les questions
  applicables ont été traitées ;
- `errors` : liste de messages d'erreur, vide en cas de succès.

`corriger_reponse` renvoie aussi `answer_codes_to_delete`, la liste des codes
effectivement supprimés. Cette liste est vide en cas d'erreur.

`ready_for_confirmation` ne signifie jamais que le profil est confirmé.
Même après une correction refusée, il peut rester `True` si les réponses
initiales étaient complètes : il faut donc vérifier `errors`. Seul le `oui`
explicite au résumé dans le terminal passe `confirme` à `True`, puis déclenche
la sauvegarde JSON.

### Question non traitée et réponse vide

Une clé absente de `reponses` correspond à une question non traitée. Une clé
présente avec la valeur `None` correspond à une question déjà traitée dont
la réponse a été laissée vide ; elle ne sera pas redemandée automatiquement.

Exemples : `{}` attend le bac, tandis que `{"bac": None}` attend la ville.
Commencer la collecte avec `{}`, et non avec `creer_profil()` : les champs
préremplis à `None` seraient considérés comme déjà traités. Le profil est
reconstruit avec `creer_profil()` et les réponses pour afficher le résumé.

### Corrections et réponses dépendantes

Si la valeur normalisée change :

- corriger `interets` supprime `precision_interets` si elle existe ;
- corriger `mobilite` supprime `autres_villes` si elle existe.

Une dépendance est supprimée même si sa valeur était `None`. Une réponse
inchangée après normalisation conserve ses dépendances. Les autres réponses
sont conservées.

Le terminal reprend ensuite les questions manquantes avec
`prochaine_question` et `traiter_reponse`, reconstruit le profil et représente
le résumé pour confirmation. Par exemple, informatique vers biologie demande
une nouvelle précision ; mobilité `oui` vers `non` efface les anciennes villes
sans les redemander ; `non` vers `oui` demande les autres villes.

## Limites actuelles

- Aucun LLM ni module RAG connecté.
- Compréhension des intérêts limitée à des mots-clés.
- Validation des réponses encore partielle.
- Aucun scoring ni recommandation de formation.
- Profil étudiant encore partiel.
- Intégration backend et format final du profil en attente de coordination
  avec P2/P5 (personnes 2 et 5).

Utiliser des données fictives pour les tests.
Le fichier profil_test.json est exclu de Git.
