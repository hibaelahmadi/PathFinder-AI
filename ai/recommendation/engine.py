# PathFinder AI - Recommendation Engine

if __package__:
    from .constraints import check_constraints
    from .ranking import rank_programs, recommendation_sort_key
else:
    from constraints import check_constraints
    from ranking import rank_programs, recommendation_sort_key


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
        key=recommendation_sort_key,
        reverse=True,
    )

    return recommendations[:top_n]
def recommend_grouped(student, programs, top_n=5):
    """Sépare les résultats lorsque la mobilité est refusée."""
    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise TypeError("top_n doit être un entier.")

    if top_n < 1:
        raise ValueError("top_n doit être supérieur ou égal à 1.")

    programs = list(programs)
    preferred_city = student.get("preferred_city")

    # Sans contrainte géographique stricte, garder le classement habituel.
    if student.get("can_relocate") is not False or not preferred_city:
        return {
            "recommendations": recommend(student, programs, top_n),
            "location_to_verify": [],
        }

    known_location = []
    unknown_location = []

    for program in programs:
        if program.get("city"):
            known_location.append(program)
        else:
            unknown_location.append(program)

    # recommend() exclut toujours les villes incompatibles,
    # les bacs incompatibles et les coûts dépassant le budget.
    return {
        "recommendations": recommend(
            student, known_location, top_n
        ),
        "location_to_verify": recommend(
            student, unknown_location, top_n
        ),
    }