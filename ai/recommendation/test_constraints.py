
from constraints import check_constraints

program = {
    "name": "Formation fictive en informatique",
    "accepted_bac_types": ["Sciences Mathématiques"],
    "city": "Marrakech",
    "annual_cost": 5000
}

# Case 1: Eligible and feasible
student1 = {
    "bac_type": "Sciences Mathématiques",
    "preferred_city": "Marrakech",
    "can_relocate": False,
    "max_annual_budget": 10000
}

# Case 2: Ineligible
student2 = {
    "bac_type": "Sciences Économiques",
    "preferred_city": "Marrakech",
    "can_relocate": False,
    "max_annual_budget": 10000
}

# Case 3: Unknown eligibility and feasibility
student3 = {
    "bac_type": None,
    "preferred_city": "Marrakech",
    "can_relocate": False,
    "max_annual_budget": None
}

for index, student in enumerate(
    [student1, student2, student3], start=1
):
    result = check_constraints(student, program)
    print(f"Étudiant {index} : {result}")

assert check_constraints(student1, program)["eligibility"] == "eligible"
assert check_constraints(student1, program)["feasibility"] == "feasible"

assert check_constraints(student2, program)["eligibility"] == "ineligible"

assert check_constraints(student3, program)["eligibility"] == "unknown"
assert check_constraints(student3, program)["feasibility"] == "unknown"

print("Tous les tests sont réussis !")
