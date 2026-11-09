
from explanations import generate_explanations

student = {
    "interests": ["informatique", "ia", "mathématiques"],
    "grades": {
        "mathématiques": 17,
        "physique": 15
    },
    "skills": ["programmation", "logique"],
    "career_goal": "ingénieur ia",
    "preferred_type": "public"
}

program = {
    "name": "Informatique",
    "interests": ["informatique", "mathématiques"],
    "required_subjects": ["mathématiques", "physique"],
    "skills": ["programmation", "logique"],
    "career_paths": ["ingénieur ia"],
    "type": "public"
}

explanations = generate_explanations(student, program)

print("Formation recommandée :", program["name"])
print("\nPourquoi cette formation ?")

for index, explanation in enumerate(explanations, start=1):
    print(f"{index}. {explanation}")

assert len(explanations) == 5
