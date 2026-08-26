"""Free legal aid eligibility — Section 12, Legal Services Authorities Act, 1987.

Purely a rules engine against NALSA's published eligibility criteria; no AI call,
no database write (the inputs here — caste category, disability, income, whether
someone is a trafficking/DV victim — are sensitive and this endpoint is deliberately
stateless so none of it gets persisted). The one contact detail given out is NALSA's
own toll-free helpline, since that's the single piece of routing information stable
and verifiable enough to hand to someone who may urgently need it — state/district
authority contact details are directed to nalsa.gov.in's own directory rather than
hardcoded here, because a wrong number handed to someone in real need is worse than
no number.
"""

from app.schemas.legal_aid import EligibilityRequest, EligibilityResponse

NALSA_HELPLINE = "15100"  # toll-free, national — the National Legal Services Authority
NALSA_WEBSITE = "https://nalsa.gov.in"

# Income ceilings under Section 12(h) vary by forum and state notification. These are
# the commonly-cited NALSA figures; state authorities can set their own (often higher)
# limits, so this is guidance, not a determination — the eligibility text says so.
SUPREME_COURT_INCOME_CEILING = 500_000
HIGH_COURT_DISTRICT_INCOME_CEILING = 300_000


def check_eligibility(req: EligibilityRequest) -> EligibilityResponse:
    matched: list[str] = []

    if req.is_woman or req.is_child:
        matched.append("Woman or child — Section 12(a)")
    if req.is_sc_st:
        matched.append("Member of Scheduled Caste / Scheduled Tribe — Section 12(b)")
    if req.is_victim_of_trafficking_or_begar:
        matched.append("Victim of trafficking or forced labour (begar) — Section 12(c)")
    if req.is_disabled:
        matched.append("Person with disability — Section 12(d)")
    if req.is_victim_of_mass_disaster:
        matched.append("Victim of mass disaster, ethnic violence, caste atrocity, flood, drought, earthquake or industrial disaster — Section 12(e)")
    if req.is_industrial_workman:
        matched.append("Industrial workman — Section 12(f)")
    if req.is_in_custody:
        matched.append("In custody, including in a protective home, juvenile home, or psychiatric hospital/nursing home — Section 12(g)")
    if req.annual_income_rupees is not None:
        ceiling = SUPREME_COURT_INCOME_CEILING if req.forum == "supreme_court" else HIGH_COURT_DISTRICT_INCOME_CEILING
        if req.annual_income_rupees <= ceiling:
            matched.append(f"Annual income within the ₹{ceiling:,} limit for {req.forum.replace('_', ' ')} legal aid — Section 12(h)")

    eligible = len(matched) > 0

    if eligible:
        guidance = (
            "Based on what you entered, you likely qualify for completely free legal aid — a lawyer "
            "provided at no cost by the government's Legal Services Authority. This is a real, funded "
            "program, separate from anything on this app. Final eligibility is decided by the Legal "
            "Services Authority itself, not by this check."
        )
    else:
        guidance = (
            "Based on what you entered, you may not automatically qualify under the standard criteria — "
            "but Legal Services Authorities do use discretion, especially for genuine hardship, and "
            "eligibility rules can vary by state. It often still costs nothing to ask."
        )

    return EligibilityResponse(
        eligible=eligible,
        matched_criteria=matched,
        guidance=guidance,
        helpline=NALSA_HELPLINE,
        website=NALSA_WEBSITE,
    )
