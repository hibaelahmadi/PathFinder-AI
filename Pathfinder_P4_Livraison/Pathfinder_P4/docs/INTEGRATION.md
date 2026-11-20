# Contrat de livraison P4

## Base et échanges

Identifiants de type chaîne : ne pas les convertir en entiers. Les identifiants `PUB`, `PRI`, `UNI`, etc. réutilisent le registre précédent. Les nouveaux identifiants sont calculés de façon déterministe à partir d’une identité normalisée. Les programmes ayant un intitulé ou un diplôme différent restent distincts. `id_crosswalk.json` documente les correspondances avec le lot Jour1 et les limites de correspondance avec les cinq anciennes fiches.

Les JSON conservent listes, booléens et null. Les listes sont sérialisées en JSON dans CSV/SQL, et affichées séparées par des points-virgules dans Excel. Les tables SQL les stockent en TEXT pour faciliter l’import sans extension. P2 peut les convertir en JSONB ou en relations après adaptation à son modèle.

Import PostgreSQL initial, dans une base de développement choisie par P2 :

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f sql/postgresql_import.sql
```

Ce script crée `pathfinder_p4`, puis des tables avec clés primaires et étrangères, dans une transaction. Il n’est volontairement pas destructif et ne remplace pas un schéma existant. Une deuxième importation dans les mêmes tables échoue plutôt que d’écraser les données. SQLite et les relations sont testés; le script PostgreSQL n’a pas été exécuté sur le serveur de l’équipe, qui n’est pas fourni.

## P3 : recherche sourcée

```python
from pathfinder_p4 import retrieve_evidence
results = await retrieve_evidence(
    "Quelles formations en informatique ?",
    filters={"city": "Marrakech", "direct_post_bac": True},
    top_k=5,
)
```

Filtres autorisés : institution_id, program_id, city, sector, field, academic_year, direct_post_bac, exploration_visible, source_id. Ils sont appliqués par égalité exacte, ou appartenance si la valeur est une liste. Un champ inconnu provoque une erreur explicite. Le filtre `academic_year` désigne l’année documentaire, pas une admission ouverte. Les paramètres sont optionnels; le défaut recherche aussi l’historique et renvoie son statut.

Pour les questions orientées suggestions, ajouter `exploration_visible=True`. Pour une question sur un avis ancien, laisser l’historique et afficher son année. Une réponse vide signifie absence de preuve récupérée, pas inexistence de formation.

Chaque passage fournit text, content_kind, institution_id, program_id, source_id, document_title, publisher, official_url, page_or_section, academic_year, checked_at, verification_date et verification_status. `verification_date=null` : aucune revue humaine signée. `checked_at` est une date de consultation. `content_kind` distingue notice structurée et extrait documentaire. Les notices livrées sont des synthèses factuelles, jamais des citations verbatim.

Le moteur livré utilise TF-IDF et une projection sémantique latente LSA de 128 dimensions, sans clé ni téléchargement de modèle. Pondération : 70 % lexicale, 30 % similarité LSA. Un minimum de recouvrement lexical réduit les réponses hors sujet. Les vecteurs ne sont pas ceux d’un modèle neuronal multilingue; français principalement, synonymes limités. Les requêtes arabes/darija ne sont pas validées. Ce choix constitue un moteur de démonstration local reproductible, pas un résultat de benchmark sémantique.

## P1 : correspondance avec la maquette

| Élément UI | Donnée / responsable |
|---|---|
| Nom de formation | programs.name |
| Établissement, ville | institutions.name, city; afficher city_status |
| Public/privé | institutions.sector; ne pas rabattre « autre » automatiquement sur privé |
| Type et durée | degree_type, duration_months, duration_scope |
| Bacs admissibles | accepted_bac_types; null → « à vérifier » |
| Frais annuels | annual_cost; null → « non renseignés » |
| Matières / enseignements | curriculum_summary si documenté; pas les mots-clés de matching |
| Intérêts, compétences | propositions P4 à valider par P5 |
| Métiers | pistes conditionnelles éditoriales; mention de poursuites nécessaires |
| Sources / date | source_id → sources; consultation distincte de validation |
| Score, facteurs, points forts | calcul par P5, jamais une constante de la maquette |
| Roadmap | pathways; étapes générales, aucune date limite inventée |

Points relevés dans la maquette : ne pas reprendre les scores 94/89/82/75, les dates de janvier à mai 2026, ni les libellés de réseaux regroupant arbitrairement des villes comme des données réelles. Le concours post-bac ENSA ne doit pas être nommé CNC après CPGE. L’étiquette « public » ne suffit pas à renseigner automatiquement zéro frais. Une spécialité d’ingénieur n’est pas forcément choisie ni garantie dès l’entrée en préparation.

## P5 : matching et contraintes

`interests`, `skills`, `career_paths` sont calculés par règles lisibles dans `taxonomy_rules.json` sur les intitulés, sans inférence sur les capacités personnelles. Ils ne prouvent pas le contenu complet du cursus ni un débouché officiel. `required_subjects` et `accepted_bac_types` restent null faute d’une normalisation validée par campagne. Les codes du vocabulaire draft-1 sont préservés. Ne pas appliquer ces listes comme critères d’éligibilité.

Le score de recherche RAG mesure la pertinence documentaire; il ne doit jamais devenir le score de compatibilité étudiant. Le champ compatibility_score des cartes vaut null pour que P5 fournisse son calcul.

## Ingestion d’autres documents

`ingest_file(path, metadata)` accepte TXT, HTML et PDF locaux. Les métadonnées obligatoires sont validées, les scripts HTML sont retirés, les PDF sont découpés page par page. Les PDF scannés sans texte provoquent une erreur demandant OCR ou transcription. Le module ne télécharge pas des URL arbitraires.

```python
import json
from pathlib import Path
from pathfinder_p4.ingest import ingest_file
chunks = ingest_file("avis.pdf", {
    "source_id": "source-a-creer-dans-sources",
    "document_title": "Titre exact de l’avis",
    "publisher": "Organisme officiel",
    "official_url": "https://URL_OFFICIELLE_A_REMPLACER",
    "checked_at": "2026-11-18",
    "academic_year": "2026-2027",
    "verification_status": "a_verifier",
})
# Ajouter la source au registre avant intégration; vérifier le texte et ses droits.
# Fusionner par chunk_id pour éviter les doublons puis reconstruire l’index.
```

Aucun LLM n’est appelé par ce module. P3 choisit son modèle et ajoute le prompt anti-hallucination. L’API de livraison est locale et ne remplace pas l’authentification, les profils ou les sessions de P2.
