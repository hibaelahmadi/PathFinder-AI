
from scoring import calculate_score


def rank_programs(student, programs, top_n=5):
    """
    Classe les formations selon leur compatibilité
    avec le profil de l'étudiant.
    """

    recommendations = []

    for program in programs:
        score = calculate_score(student, program)

        recommendation = {
            "program": program["name"],
            "score": score
        }

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations[:top_n]
