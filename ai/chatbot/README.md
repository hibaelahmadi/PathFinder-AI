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

Les tests utilisent des réponses fictives et ne sauvegardent aucun profil.
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
et la sauvegarde sont gérés par `chatbot.py`. La confirmation est aussi
exposée par l’adaptateur synchrone décrit ci-dessous.

| Fonction | Paramètres | Résultat |
| --- | --- | --- |
| `choisir_question_interets(interets)` | Texte des intérêts, ou `None`. | Texte de la question de précision : informatique, biologie ou question générique. La recherche des mots-clés ignore les majuscules. |
| `creer_profil()` | Aucun. | Nouveau dictionnaire contenant les onze champs du profil à `None` et `confirme` à `False`. |
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

## Champs préparés pour le profil

Les trois champs suivants sont présents dans `creer_profil()`. Leur structure
prévue est :

| Champ | Valeur prévue |
| --- | --- |
| `notes` | Objet matière → nombre entre 0 et 20 inclus, ou `None` si non renseigné. Omettre les matières sans note ; une note de `0` reste une vraie valeur. |
| `budget_annuel_max` | Nombre positif ou nul, ou `None` si non renseigné. Montant annuel maximal en DH pour les frais de scolarité uniquement, hors frais d'inscription, logement et transport. Un budget de `0` reste une vraie valeur. |
| `type_etablissement` | `"public"`, `"prive"` ou `None` (sans préférence ou non renseigné). |

Leurs textes sont préparés dans `QUESTIONS`, avec Entrée pour passer, mais
leurs questions ne sont pas encore intégrées au parcours. Ils apparaissent
actuellement à `null` dans le profil JSON sauvegardé par le terminal et dans
`profile` renvoyé par l'adaptateur. P2 a confirmé ces trois champs ; sa validation
backend doit encore être adaptée. Aucune logique backend n'est ajoutée ici.

Les codes des matières attendent la validation P4/P5 : aucune liste de
matières n'est définie. Les validations isolées ne collectent pas encore
ces informations et ne construisent pas l'objet `notes`.

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


## Adaptateur synchrone pour l'intégration

Depuis la racine du dépôt, l'import est :

```python
from ai.chatbot.questionnaire import traiter_questionnaire

resultat = traiter_questionnaire(None, "start")
etat = resultat["etat"]
resultat = traiter_questionnaire(
    etat, "answer", {"question_code": "bac", "answer_text": " Sciences "}
)
# La prochaine question réelle est ville_souhaitee, pas mobilite.
```

`traiter_questionnaire(etat, action, reponse=None)` est une fonction publique
**synchrone** : appel direct, sans `await`. Elle réutilise `traiter_reponse`
et `corriger_reponse`. Aucun accès à une base, aucune sauvegarde, aucun
`input`/`print` et aucun appel LLM ne sont effectués. Le terminal conserve son
fonctionnement actuel et n'utilise pas cet adaptateur.

### Entrées

`answers` est un **dictionnaire indexé par question_code**, conformément au
contrat P2. `reponse` est un dictionnaire pour `answer` et `correct`.

- `etat` : `None` pour démarrer, sinon dictionnaire contenant `status`
  (`in_progress` ou `completed`), `expected_question_code` (code ou `None`)
  et `answers` (dictionnaire, vide au démarrage).
- Chaque clé de `answers` doit correspondre au `question_code` de son entrée.
  Chaque entrée contient `question_code`, `question_text`,
  `answer_text` original et éventuellement `answer_value`.
- `reponse` accepte `question_code`, `question_text`, `answer_text` et
  `answer_value` facultatif, par exemple :
  `{"question_code": "bac", "question_text": "Quelle est ta série de bac ?", "answer_text": "Sciences mathématiques", "answer_value": null}`
  (notation JSON). `question_text` peut être omis : il est toujours recalculé.
  Pour les autres actions, laisser `reponse=None`.

Le texte original est conservé exactement. Les valeurs sont recalculées depuis
`answer_text` avec la validation commune, y compris pour les réponses de l'état.
Les `answer_value`, textes de questions et `expected_question_code` reçus ne
font pas autorité. Les états réussis contiennent les textes de questions et
valeurs recalculés ; les champs supplémentaires ne sont pas retransmis.
Les codes inconnus, clés incohérentes avec `question_code`, réponses stockées
invalides, statuts inconnus
et autres villes incompatibles avec la mobilité sont refusés.

L'état représente un instantané, pas un historique vérifiable. Il peut avoir
des questions manquantes après correction ; la prochaine question est toujours
recalculée depuis les réponses présentes. Une nouvelle action `answer` doit
respecter cet ordre. Le backend devra fournir un état de confiance et gérer
la persistance ainsi que les accès à l'entretien.

Une entrée absente signifie « non traité ». Une entrée présente avec
`answer_text` vide ou composé d'espaces est traitée et sa valeur normalisée
est `None`, sauf pour la mobilité qui exige une valeur autorisée. Ne pas
préremplir le dictionnaire avec des entrées vides pour les questions non traitées.

### Actions

| Action | Comportement |
| --- | --- |
| `start` | Initialise depuis `None` ou un état `in_progress` sans réponses. Refuse de réinitialiser un entretien contenant des réponses ou déjà terminé. |
| `answer` | Répond uniquement à la question réellement attendue, dans un entretien `in_progress`. La dernière réponse laisse ce statut et ne confirme rien. |
| `correct` | Corrige une question déjà traitée via `corriger_reponse`, dans un entretien `in_progress`. Transmet les suppressions dépendantes et recalcule la prochaine question. |
| `confirm` | Réussit seulement en `in_progress` lorsque toutes les questions applicables sont traitées. Passe à `completed` et confirme le profil. |
| `reopen` | Réussit seulement depuis `completed`. Conserve les réponses, revient à `in_progress` et retire la confirmation. |

Après `completed`, `answer` et `correct` sont refusés avant `reopen`.
Un second `confirm` et un `reopen` en cours d'entretien sont également refusés.

### Sortie commune à toutes les actions

| Champ | Contenu |
| --- | --- |
| `etat` | Nouvel état canonique en cas de succès ; copie profonde exacte de l'état initial en cas d'erreur. |
| `next_question` | Question recalculée (`question_code`, `question_text`) ou `None`. |
| `answers_to_save` | Liste contenant seulement la réponse acceptée par `answer` ou `correct`, avec texte original, texte de question canonique et valeur normalisée. Vide pour les autres actions. Ce sont des données à persister par l'appelant, pas une sauvegarde effectuée. |
| `answer_codes_to_delete` | Codes effectivement supprimés après correction ; liste vide sinon. |
| `profile` | Instantané de `creer_profil()` enrichi des valeurs normalisées et de `confirme`. Inclut les trois champs préparés décrits ci-dessus, actuellement à `null`. |
| `profile_confirmed` | Confirmation actuelle : `True` pour un état `completed` valide, `False` sinon. |
| `errors` | Liste de messages, vide en cas de succès. |

Toute erreur conserve l'état initial, sans réponse à sauvegarder ni suppression
et sans confirmation nouvelle. Si un entretien était déjà confirmé et que
l'action est refusée, sa confirmation reste `True`. Pour un état d'entrée
malformé, le profil est seulement une projection des réponses lisibles et
valides, non confirmée : vérifier `errors` avant d'exploiter le résultat.
Les objets d'entrée, y compris leurs éléments imbriqués, ne sont jamais modifiés.
Les objets retournés n'en partagent pas les structures mutables.

### Trois retours JSON complets

Exemples générés depuis la fonction avec des données fictives. Les réponses
vides sont volontaires et restent distinctes des réponses absentes.

#### confirm réussi

```json
{
  "etat": {
    "status": "completed",
    "expected_question_code": null,
    "answers": {
      "bac": {
        "question_code": "bac",
        "question_text": "Quelle est ta série de bac ? ",
        "answer_text": "",
        "answer_value": null
      },
      "ville_souhaitee": {
        "question_code": "ville_souhaitee",
        "question_text": "Dans quelle ville souhaites-tu étudier ? ",
        "answer_text": "",
        "answer_value": null
      },
      "interets": {
        "question_code": "interets",
        "question_text": "Quelles matières ou activités aimes-tu ? ",
        "answer_text": "",
        "answer_value": null
      },
      "precision_interets": {
        "question_code": "precision_interets",
        "question_text": "Peux-tu donner un exemple d'activité que tu aimes ? Tu peux passer avec Entrée. ",
        "answer_text": "",
        "answer_value": null
      },
      "mobilite": {
        "question_code": "mobilite",
        "question_text": "Acceptes-tu d'étudier dans une autre ville ? (oui / non / je ne sais pas) ",
        "answer_text": "non",
        "answer_value": "non"
      },
      "objectif": {
        "question_code": "objectif",
        "question_text": "Quel métier ou domaine aimerais-tu explorer ? Tu peux répondre « je ne sais pas ». ",
        "answer_text": "",
        "answer_value": null
      },
      "competences_declarees": {
        "question_code": "competences_declarees",
        "question_text": "Dans quelles activités te sens-tu à l'aise ? Par exemple : analyser, créer, communiquer, aider, résoudre des problèmes. Tu peux passer avec Entrée. ",
        "answer_text": "",
        "answer_value": null
      }
    }
  },
  "next_question": null,
  "answers_to_save": [],
  "answer_codes_to_delete": [],
  "profile": {
    "notes": null,
    "budget_annuel_max": null,
    "type_etablissement": null,
    "bac": null,
    "ville_souhaitee": null,
    "interets": null,
    "precision_interets": null,
    "mobilite": "non",
    "autres_villes": null,
    "objectif": null,
    "competences_declarees": null,
    "confirme": true
  },
  "profile_confirmed": true,
  "errors": []
}
```

#### reopen réussi

```json
{
  "etat": {
    "status": "in_progress",
    "expected_question_code": null,
    "answers": {
      "bac": {
        "question_code": "bac",
        "question_text": "Quelle est ta série de bac ? ",
        "answer_text": "",
        "answer_value": null
      },
      "ville_souhaitee": {
        "question_code": "ville_souhaitee",
        "question_text": "Dans quelle ville souhaites-tu étudier ? ",
        "answer_text": "",
        "answer_value": null
      },
      "interets": {
        "question_code": "interets",
        "question_text": "Quelles matières ou activités aimes-tu ? ",
        "answer_text": "",
        "answer_value": null
      },
      "precision_interets": {
        "question_code": "precision_interets",
        "question_text": "Peux-tu donner un exemple d'activité que tu aimes ? Tu peux passer avec Entrée. ",
        "answer_text": "",
        "answer_value": null
      },
      "mobilite": {
        "question_code": "mobilite",
        "question_text": "Acceptes-tu d'étudier dans une autre ville ? (oui / non / je ne sais pas) ",
        "answer_text": "non",
        "answer_value": "non"
      },
      "objectif": {
        "question_code": "objectif",
        "question_text": "Quel métier ou domaine aimerais-tu explorer ? Tu peux répondre « je ne sais pas ». ",
        "answer_text": "",
        "answer_value": null
      },
      "competences_declarees": {
        "question_code": "competences_declarees",
        "question_text": "Dans quelles activités te sens-tu à l'aise ? Par exemple : analyser, créer, communiquer, aider, résoudre des problèmes. Tu peux passer avec Entrée. ",
        "answer_text": "",
        "answer_value": null
      }
    }
  },
  "next_question": null,
  "answers_to_save": [],
  "answer_codes_to_delete": [],
  "profile": {
    "notes": null,
    "budget_annuel_max": null,
    "type_etablissement": null,
    "bac": null,
    "ville_souhaitee": null,
    "interets": null,
    "precision_interets": null,
    "mobilite": "non",
    "autres_villes": null,
    "objectif": null,
    "competences_declarees": null,
    "confirme": false
  },
  "profile_confirmed": false,
  "errors": []
}
```

#### Erreur de validation : la ville est attendue

```json
{
  "etat": {
    "status": "in_progress",
    "expected_question_code": "ville_souhaitee",
    "answers": {
      "bac": {
        "question_code": "bac",
        "question_text": "Quelle est ta série de bac ?",
        "answer_text": "Sciences mathématiques",
        "answer_value": null
      }
    }
  },
  "next_question": {
    "question_code": "ville_souhaitee",
    "question_text": "Dans quelle ville souhaites-tu étudier ? "
  },
  "answers_to_save": [],
  "answer_codes_to_delete": [],
  "profile": {
    "notes": null,
    "budget_annuel_max": null,
    "type_etablissement": null,
    "bac": "Sciences mathématiques",
    "ville_souhaitee": null,
    "interets": null,
    "precision_interets": null,
    "mobilite": null,
    "autres_villes": null,
    "objectif": null,
    "competences_declarees": null,
    "confirme": false
  },
  "profile_confirmed": false,
  "errors": [
    "Le code ne correspond pas à la question attendue."
  ]
}
```
