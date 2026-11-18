"""Classement des formations par compatibilité."""

if __package__:
    from .explanations import generate_explanations
    from .scoring import calculate_score
else:
    from explanations import generate_explanations
    from scoring import calculate_score


def recommendation_sort_key(item):
    score = item["score"]
    return (
        score is not None,
        score if score is not None else 0,
    )


def rank_programs(student, programs, top_n=5):
    if isinstance(top_n, bool) or not isinstance(top_n, int):
        raise TypeError("top_n doit être un entier.")

    if top_n < 1:
        raise ValueError("top_n doit être supérieur ou égal à 1.")

    recommendations = []

    for program in programs:
        recommendations.append({
            "program_id": program.get("id"),
            "program_code": program.get("code"),
            "program": program["name"],
            "score": calculate_score(student, program),
            "explanations": generate_explanations(student, program),
        })

    recommendations.sort(
        key=recommendation_sort_key,
        reverse=True,
    )

    return recommendations[:top_n]