
# PathFinder AI - Orientation Constraints


def check_constraints(student, program):
    """
    Check academic eligibility and practical feasibility.

    The program must contain:
    - accepted_bac_types: list or None
    - city: string
    - annual_cost: number or None

    The student must contain:
    - bac_type: string or None
    - preferred_city: string or None
    - can_relocate: bool or None
    - max_annual_budget: number or None
    """

    eligibility = "eligible"
    feasibility = "feasible"
    reasons = []

    # 1. Check baccalaureate eligibility
    accepted = program.get("accepted_bac_types")
    bac_type = student.get("bac_type")

    if accepted is None or bac_type is None:
        eligibility = "unknown"
        reasons.append("Type de bac : éligibilité à vérifier.")

    elif bac_type not in accepted:
        eligibility = "ineligible"
        reasons.append("Type de bac non accepté.")

    # 2. Check geographical feasibility
    preferred_city = student.get("preferred_city")
    program_city = program.get("city")
    can_relocate = student.get("can_relocate")

    if preferred_city and program_city:
        if preferred_city != program_city:
            if can_relocate is False:
                feasibility = "not_feasible"
                reasons.append(
                    "La formation est située hors de la ville souhaitée."
                )
            elif can_relocate is None:
                feasibility = "unknown"
                reasons.append("Mobilité à vérifier.")
    else:
        feasibility = "unknown"
        reasons.append("Localisation à vérifier.")

    # 3. Check budget feasibility
    budget = student.get("max_annual_budget")
    cost = program.get("annual_cost")

    if budget is None or cost is None:
        if feasibility != "not_feasible":
            feasibility = "unknown"
        reasons.append("Budget ou coût de formation à vérifier.")

    elif cost > budget:
        feasibility = "not_feasible"
        reasons.append("Le coût dépasse le budget annuel.")

    return {
        "eligibility": eligibility,
        "feasibility": feasibility,
        "reasons": reasons
    }
