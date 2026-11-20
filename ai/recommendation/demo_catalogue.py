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
    "bac": "Sciences mathématiques",
    "ville_souhaitee": "Rabat",
    "mobilite": "oui",
    "categories_interets": ["informatique"],
    "categories_competences": ["programmation"],
    "code_metier": "ingenieur_informatique",
    "notes": None,
    "budget_annuel_max": None,
    "type_etablissement": "prive",
    "confirme": True,
}

student = adapt_student_profile(profile)
results = recommend(student, adapted_programs, top_n=5)

for position, result in enumerate(results, start=1):
    print(f"\n{position}. {result['program']}")
    print("Identifiant :", result["program_id"])
    print("Score :", result["score"])
    print("Explications :", result["explanations"])
    print("Points à vérifier :", result["constraints"]["reasons"])