# Pathfinder AI — Livraison P4

18 novembre 2026 · Hafssa · Data Engineering & RAG · Version 1.0.0

Ce dossier rassemble le catalogue documentaire marocain, les sources, les exports relationnels, le pipeline d’ingestion local, la recherche hybride avec vecteurs et les interfaces pour P2/P3/P5. La couverture nationale et les admissions 2026–2027 ne sont pas intégralement vérifiées. Les données manquantes sont explicites et les anciennes mentions sont conservées à part.

## À ouvrir

- `Pathfinder_P4_Catalogue.xlsx` : lecture, filtres, formations, établissements par secteur, historique et sources.
- `manifest.json` : nombres exacts et périmètre de cette version.
- `data/programs_exploration.json` : sélection prudente de parcours dont la voie post-bac est documentée. Ouverture actuelle et éligibilité individuelle restent à vérifier.
- `data/programs.json` : catalogue documentaire complet, incluant niveaux supérieurs et historique; ne pas publier tout comme des admissions post-bac.
- `pathfinder.sqlite` : base locale immédiatement consultable.
- `sql/postgresql_import.sql` : import initial dans un schéma PostgreSQL dédié.
- `documents/chunks.jsonl` et `index/` : notices factuelles sourcées et index prêt pour la recherche.
- `docs/INTEGRATION.md` : contrat P2/P3/P5 et correspondance avec la maquette Gemini consultée.
- `docs/QUALITE.md` : tests, limites de couverture et règles de publication.

## Démarrage Python, sans clé d’API

Python 3.11 ou ultérieur. Depuis le dossier extrait `Pathfinder_P4` :

```bash
python -m venv .venv
```

Windows PowerShell : `.venv\Scripts\Activate.ps1`

macOS/Linux : `source .venv/bin/activate`

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pathfinder_p4.cli search "ENSA Marrakech cycle préparatoire"
python -m uvicorn pathfinder_p4.api:app --host 127.0.0.1 --port 8000
```

Documentation de l’API locale : `http://127.0.0.1:8000/docs`.
Les données restent dans le dossier extrait : conserver cette arborescence et l’installation éditable. Ce livrable n’est pas un paquet wheel autonome contenant les données.

## Répartition pour l’équipe

**P2** : intégrer le module Python ou reprendre les routes FastAPI proposées. Le schéma PostgreSQL est un schéma de livraison isolé, pas une migration des tables existantes de P2.

**P3** : appeler `await retrieve_evidence(query, filters, top_k)` et appliquer le prompt de `docs/RAG_PROMPT.txt`. Les résultats contiennent les sources et les limites. La génération de texte finale relève du chatbot de P3.

**P5** : utiliser les intérêts et compétences comme propositions éditoriales. Le vocabulaire demeure `draft-1`, non approuvé dans les échanges retrouvés. Ne pas fabriquer un score de probabilité d’admission. Les scores de compatibilité ne sont pas préremplis.

**P1** : afficher les données de `card(program_id)` et les warnings. Ne pas afficher un badge « vérifié » à partir de la seule date de consultation.

## Règles à conserver

1. `annual_cost` = frais de scolarité annuels en MAD uniquement; exclut inscription, logement, transport et fournitures.
2. `null` signifie inconnu. Il ne signifie ni gratuit, ni sans condition, ni refus.
3. Une durée de cycle ingénieur de 36 mois n’est pas nécessairement une formation accessible directement après le bac.
4. Une liste d’établissements, une accréditation, une reconnaissance de l’État et un avis d’admission prouvent des choses différentes.
5. Les adresses de composantes universitaires peuvent être celles du rattachement; les réseaux ne sont pas des campus.
6. L’année de consultation n’est pas l’année d’admission. Aucune campagne actuelle n’est déclarée entièrement validée dans cette livraison.
7. Les filières d’anciens registres peuvent être fermées ou renommées. L’absence d’un renouvellement dans la collecte ne prouve pas sa non-existence.

## Mise à jour

Les JSON de `data/` sont les données de référence. Les CSV et Excel sont des exports. Une modification manuelle de l’Excel ne met pas automatiquement à jour JSON ou SQLite.
Après modification contrôlée des données, exécuter le pipeline de validation, nettoyage des notices, export relationnel et reconstruction des vecteurs :

```bash
python -m pathfinder_p4.pipeline
python -m unittest discover -s tests -v
```

L’index refuse de charger si son empreinte ne correspond plus au corpus.
