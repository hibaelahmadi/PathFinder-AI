# Rapport de qualité et périmètre

Livraison du 18 novembre 2026. Les contrôles techniques ne constituent pas une certification administrative des formations.

## Contenu livré

| Objet | Nombre | Interprétation |
|---|---:|---|
| Références institutionnelles | 633 | Établissements, composantes, centres et réseaux; identités historiques et alias possibles |
| Fiches de formations ou cycles | 1 699 | Intitulés documentés, incluant historique et études après bac+2/+3 |
| Mentions d’accréditation | 2 932 | Registre cumulatif ministériel 2024/2025; renouvellements conservés |
| Fiches sélectionnées pour exploration | 87 | Voie bac documentée, réserves visibles; pas admission actuelle certifiée |
| Sources documentaires | 40 | Pages et registres officiels, de périodes différentes |
| Notices RAG | 2 332 | Synthèses factuelles et notices d’annuaire |
| Admissions actuelles intégralement vérifiées | 0 | Les neuf notices d’admission sont générales, sans campagne validée |
| Tarifs annuels actuels confirmés | 0 | annual_cost reste null |

## Collecte et nettoyage

Le registre national précédent a été repris avec ses identifiants et sa période : 165 références du public universitaire, 131 du registre privé, 83 composantes, 67 centres CPGE, 50 centres BTS et 28 mentions historiques hors universités. Les parents universitaires n’ont pas été ajoutés artificiellement comme écoles supplémentaires.

Le registre des accréditations privées est identifié comme état 2024/2025. Ses 13 256 lignes indexées ont été recueillies, sans trou dans la numérotation. Une extraction à dix colonnes a produit 2 932 mentions structurellement valides, zéro ligne rejetée par ce contrôle. Les noms, options, diplômes, durées et périodes sont conservés. Cinq répétitions strictement identiques du registre sont préservées dans l’historique pour la traçabilité; elles ne créent pas des programmes distincts dans le catalogue dédupliqué.

Le regroupement porte sur identité institutionnelle, ville, intitulé et diplôme normalisés. Les accents, espaces et variations de casse sont neutralisés pour la clé, mais le libellé de source reste visible. Aucun rapprochement flou n’est utilisé. Les rapprochements d’établissements ne sont faits que par nom/ville exacts normalisés, ou par sigle/ville lorsque le résultat est unique. Les variations non résolues demeurent des références distinctes.

Treize groupes comportent plusieurs mentions de la même année avec des options, durées ou échéances différentes. Ils portent `conflit_registre_a_resoudre`, leurs options consolidées sont laissées vides et ils sont exclus de l’exploration. Toutes les variantes restent dans `accreditation_history`.

L’échéance publiée la plus récente n’est jamais qualifiée de reconnaissance actuelle. Les périodes écoulées portent `echeance_ancienne_renouvellement_inconnu`. Les périodes non atteintes portent `echeance_publiee_non_atteinte`, avec avertissement sur l’activité et les admissions.

Les nouvelles fiches générales complètent notamment Al Akhawayn, FSSM, Faculté des sciences de Rabat, ENS et FLSH Marrakech, ENA Meknès, ISIC, ISCAE et une offre réseau OFPPT. Une liste de licences sans preuve de niveau d’entrée n’est pas transformée automatiquement en admission directe au bac.

## Vérifications exécutées

- 20 tests automatiques réussis : identifiants, clés étrangères, vocabulaire, valeurs inconnues, durées, filtres, contrat asynchrone, API, ingestion, découpage et cas sans résultat.
- Validation JSON Schema de chacune des 1 699 fiches.
- SQLite : `integrity_check=ok`, zéro violation de clé étrangère.
- Cinq essais de recherche sur des institutions ciblées, consignés dans `retrieval_smoke_tests.json`. Ce sont des essais de fonctionnement, pas une évaluation de pertinence sur un jeu indépendant.
- Excel : 14 onglets exportés, aperçu visuel de chaque onglet examiné, compteurs recoupés avec les JSON et absence d’erreurs de formule détectées. Le classeur est principalement un export de données, sans calculs de recommandation.
- Les dépendances réellement utilisées figurent dans `test_environment.json`. Les commandes et résultats sont conservés dans `test_results.txt`.

## Ce qui n’est pas attesté

La collecte n’est pas exhaustive au niveau national pour 2026–2027. Les listes de campus ISPITS, centres OFPPT/CMC/ISTA et leurs spécialités locales, écoles militaires, autres départements ministériels et certains établissements à statut particulier restent incomplets. La présence d’une école dans le registre ne signifie pas qu’une fiche de chacune de ses formations a été collectée.

Les conditions annuelles détaillées, bacs autorisés, seuils, quotas, dates limites, pièces à fournir et tarifs ne sont pas complétés artificiellement. Les contenus pédagogiques détaillés sont renseignés seulement pour une partie des fiches. Les mots-clés éditoriaux ne remplacent pas des programmes de cours officiels.

Les pages institutionnelles générales peuvent être anciennes malgré leur disponibilité. Les adresses de rattachement ne prouvent pas le campus d’enseignement. Les établissements fermés ou renommés sont expressément présents dans le registre ministériel historique. La comparaison d’accréditation et reconnaissance d’État nécessiterait des sources distinctes supplémentaires.

Les vecteurs LSA sont locaux et non neuronaux. Pas de benchmark français/arabe/darija, pas de test utilisateur, pas d’intégration au serveur de P2 ni au LLM de P3, pas d’exécution du SQL PostgreSQL sur l’infrastructure de l’équipe. Les scores P5 ne font pas partie de P4.

La maquette Gemini a été consultée; elle sert à adapter les champs, jamais comme source d’informations sur les écoles.
