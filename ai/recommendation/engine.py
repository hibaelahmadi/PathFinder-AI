# PathFinder AI - Recommendation Engine

from constraints import check_constraints
from ranking import rank_programs


def recommend(student, programs, top_n=5):
    """
    Filtre les formations incompatibles, puis classe
    les formations restantes.

    Les contraintes inconnues sont signalées dans
    le résultat, sans exclure la formation.
    """
    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise TypeError("top_n doit être un entier.")

    if top_n < 1:
        raise ValueError("top_n doit être supérieur ou égal à 1.")

    recommendations = []

    for program in programs:
        constraints = check_constraints(student, program)

        if constraints["eligibility"] == "ineligible":
            continue

        if constraints["feasibility"] == "not_feasible":
            continue

        # Réutilise le calcul du score et des explications.
        recommendation = rank_programs(
            student,
            [program],
            top_n=1
        )[0]

        recommendation["constraints"] = constraints
        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations[:top_n]