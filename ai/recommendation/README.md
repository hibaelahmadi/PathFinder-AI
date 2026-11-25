# Moteur de recommandation PathFinder AI

Le moteur filtre les formations incompatibles, calcule leurs points
de correspondance et fournit des explications.

Le score n’est pas une probabilité d’admission.

## Utilisation

Lancer Python depuis la racine du dépôt.

```python
from ai.recommendation.adapters import (
    adapt_student_profile,
    adapt_p4_program,
)
from ai.recommendation.engine import recommend_grouped

student = adapt_student_profile(profile)

institutions_by_id = {
    item["institution_id"]: item
    for item in institutions
}

programs = [
    adapt_p4_program(
        program,
        institutions_by_id[program["institution_id"]],
    )
    for program in exploration_programs
]

results = recommend_grouped(student, programs, top_n=5)
```

`profile` est le profil du questionnaire. `exploration_programs`
et `institutions` sont les listes chargées depuis les JSON P4.

Le backend doit vérifier que le profil est confirmé et valider
les types et les codes avant l’appel au moteur.

## Correspondances du profil

| Questionnaire | Moteur |
|---|---|
| code_bac | bac_type |
| bac | bac_text |
| ville_souhaitee | preferred_city |
| mobilite | can_relocate |
| notes | grades |
| budget_annuel_max | max_annual_budget |
| type_etablissement | preferred_type |
| categories_interets | interests |
| categories_competences | skills |
| code_metier | career_goal |

Mobilité : "oui" devient True, "non" devient False,
une réponse inconnue devient None.

Les textes libres sont conservés séparément.
Les codes utilisent le vocabulaire draft-1.

## Calcul du score

| Critère | Maximum |
|---|---:|
| Intérêts | 30 points |
| Résultats scolaires | 25 points |
| Compétences | 20 points |
| Objectif professionnel | 15 points |
| Type d’établissement | 10 points |

Les poids restent fixes. Un critère inconnu n’apporte aucun point.
Si aucun critère n’est calculable, le score vaut None.
Un score faible peut donc refléter des données incomplètes.

## Contraintes

Une formation est exclue en cas de :
- bac explicitement incompatible ;
- coût annuel supérieur au budget déclaré ;
- ville différente lorsque la mobilité est refusée.

Une contrainte inconnue conserve la formation avec un avertissement.

Le budget concerne uniquement la scolarité annuelle en DH,
hors inscription, logement et transport.
Zéro est une valeur réelle ; None signifie inconnu.

## Résultats groupés

`recommend_grouped()` renvoie :

```json
{
  "recommendations": [],
  "location_to_verify": []
}
```

Lorsque la mobilité est refusée et qu’une ville est renseignée :
- recommendations : formations avec ville compatible ;
- location_to_verify : formations avec localisation inconnue.

Sinon, le classement habituel est renvoyé dans recommendations.
top_n s’applique séparément à chaque liste.

Chaque résultat contient :
program_id, program_code, program, score, explanations et constraints.

recommend(student, programs, top_n=5) reste disponible
et renvoie une seule liste.

Une liste peut être vide. Un score inconnu devient null en JSON.

## Catalogue P4

Dossier :
Pathfinder_P4_Livraison/Pathfinder_P4/data/

Fichiers utilisés :
- programs_exploration.json
- institutions.json

Les identifiants P4 restent des chaînes.
Les sources et statuts sont conservés par l’adaptateur, mais ne sont
pas tous inclus dans les résultats : le backend doit les rattacher
aux fiches à partir des identifiants.

Les associations intérêts, compétences et métiers sont éditoriales.
Les admissions actuelles ne sont pas garanties.
Une ville de registre ne garantit pas à elle seule un campus actuel.

## Vérification

Depuis la racine du dépôt :

```powershell
python -m unittest discover -s ai/recommendation -p "test_*.py" -v
python -m ai.recommendation.demo_catalogue
```

La démonstration nécessite les fichiers P4 présents localement.

## Erreurs

top_n doit être un entier supérieur ou égal à 1.
Une valeur invalide déclenche TypeError ou ValueError.

Le moteur ne renvoie pas de statut HTTP.
Le backend doit valider les entrées et gérer les exceptions.