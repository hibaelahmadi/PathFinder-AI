import json
from pathlib import Path

from ai.recommendation.adapters import (
    adapt_p4_program,
    adapt_student_profile,
)
from ai.recommendation.engine import recommend


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Pathfinder_P4_Livraison/Pathfinder_P4/data"

programs = json.loads(
    (DATA / "programs_exploration.json").read_text(encoding="utf-8")
)
institutions = {
    item["institution_id"]: item
    for item in json.loads(
        (DATA / "institutions.json").read_text(encoding="utf-8")
    )
}

adapted_programs = [
    adapt_p4_program(program, institutions[program["institution_id"]])
    for program in programs
]

# Profil fictif : ce n'est pas encore le cas exact testé par Nada.
profile = {
    "notes": {"mathematiques": 0.0},
    "budget_annuel_max": 0.0,
    "type_etablissement": "prive",
    "bac": "Sciences mathématiques",
    "ville_souhaitee": "Rabat",
    "interets": "Je programme",
    "precision_interets": "Des applications",
    "mobilite": "non",
    "autres_villes": None,
    "objectif": "Ingénieur informatique",
    "competences_declarees": "Je sais programmer",
    "confirme": True,
    "categories_interets": ["informatique"],
    "categories_competences": ["programmation"],
    "code_metier": "ingenieur_informatique",
}

student = adapt_student_profile(profile)
results = recommend(student, adapted_programs, top_n=5)

for position, result in enumerate(results, start=1):
    print(f"\n{position}. {result['program']}")
    print("Identifiant :", result["program_id"])
    print("Score :", result["score"])
    print("Explications :", result["explanations"])
    print("Points à vérifier :", result["constraints"]["reasons"])

all_results = recommend(
    student,
    adapted_programs,
    top_n=len(adapted_programs),
)

programs_by_id = {
    program["id"]: program
    for program in adapted_programs
}

known_city = [
    result
    for result in all_results
    if programs_by_id[result["program_id"]].get("city") is not None
]

unknown_city = [
    result
    for result in all_results
    if programs_by_id[result["program_id"]].get("city") is None
]

print("\n--- Diagnostic du filtrage ---")
print("Formations conservées :", len(all_results))
print("Avec ville exploitable :", len(known_city))
print("Avec localisation à vérifier :", len(unknown_city))

print("\nPremières formations avec ville exploitable :")
for result in known_city[:5]:
    program = programs_by_id[result["program_id"]]
    print(
        result["program"],
        "| Ville :", program["city"],
        "| Score :", result["score"],
    )