import json
from app.agents.state import AgentState
from app.services.claude import get_claude_response

TEMPLATES = {
    "legal_notice_general": {"id": "legal_notice_general", "name": "Legal Notice (General)", "category": "Notices", "description": "General legal notice for any dispute or grievance", "fields": ["sender_name", "sender_address", "recipient_name", "recipient_address", "subject", "dispute_details", "demand", "response_deadline_days"], "applicable_law": "General civil law"},
    "cheque_bounce_138": {"id": "cheque_bounce_138", "name": "Cheque Bounce Notice (Sec 138 NI Act)", "category": "Notices", "description": "Statutory notice for dishonoured cheque under Section 138", "fields": ["sender_name", "sender_address", "drawer_name", "drawer_address", "cheque_number", "cheque_date", "cheque_amount", "bank_name", "dishonour_date", "dishonour_reason"], "applicable_law": "Section 138, Negotiable Instruments Act, 1881"},
    "demand_notice": {"id": "demand_notice", "name": "Recovery/Demand Notice", "category": "Notices", "description": "Formal demand for payment of outstanding dues", "fields": ["sender_name", "sender_address", "debtor_name", "debtor_address", "amount_due", "due_since_date", "nature_of_dues", "payment_deadline_days"], "applicable_law": "Indian Contract Act, 1872"},
    "rental_agreement": {"id": "rental_agreement", "name": "Rental Agreement", "category": "Agreements", "description": "Residential or commercial property rental agreement", "fields": ["landlord_name", "landlord_address", "tenant_name", "tenant_address", "property_address", "monthly_rent", "security_deposit", "lease_start_date", "lease_duration_months", "lock_in_period_months"], "applicable_law": "Transfer of Property Act, 1882"},
    "leave_license": {"id": "leave_license", "name": "Leave & License Agreement", "category": "Agreements", "description": "Leave and license agreement used in Maharashtra and other states", "fields": ["licensor_name", "licensor_address", "licensee_name", "licensee_address", "property_address", "monthly_compensation", "security_deposit", "start_date", "duration_months"], "applicable_law": "Maharashtra Rent Control Act; Indian Easements Act"},
    "sale_deed": {"id": "sale_deed", "name": "Sale Deed", "category": "Property", "description": "Transfer of property ownership", "fields": ["seller_name", "seller_address", "buyer_name", "buyer_address", "property_description", "property_area", "sale_consideration", "advance_paid", "balance_amount", "possession_date", "registration_date"], "applicable_law": "Transfer of Property Act, 1882; Registration Act, 1908"},
    "agreement_to_sell": {"id": "agreement_to_sell", "name": "Agreement to Sell", "category": "Property", "description": "Preliminary agreement for property sale before execution of sale deed", "fields": ["seller_name", "seller_address", "buyer_name", "buyer_address", "property_description", "agreed_price", "token_amount", "balance_due_date", "conditions"], "applicable_law": "Transfer of Property Act, 1882; Specific Relief Act, 1963"},
    "employment_contract": {"id": "employment_contract", "name": "Employment Agreement", "category": "Corporate", "description": "Employment agreement between employer and employee", "fields": ["company_name", "company_address", "employee_name", "employee_address", "designation", "department", "start_date", "monthly_salary", "probation_months", "notice_period_months", "work_location"], "applicable_law": "Industrial Disputes Act; Contract Labour Act"},
    "nda": {"id": "nda", "name": "Non-Disclosure Agreement (NDA)", "category": "Corporate", "description": "NDA to protect confidential business information", "fields": ["party_a_name", "party_a_address", "party_b_name", "party_b_address", "purpose", "confidential_information_description", "duration_years", "governing_law_state"], "applicable_law": "Indian Contract Act, 1872"},
    "mou": {"id": "mou", "name": "Memorandum of Understanding (MOU)", "category": "Corporate", "description": "Non-binding agreement outlining terms of a business relationship", "fields": ["party_a_name", "party_a_address", "party_b_name", "party_b_address", "purpose", "scope_of_collaboration", "duration", "governing_law_state"], "applicable_law": "Indian Contract Act, 1872"},
    "partnership_deed": {"id": "partnership_deed", "name": "Partnership Deed", "category": "Corporate", "description": "Partnership deed for setting up a business partnership", "fields": ["firm_name", "business_address", "partner_1_name", "partner_1_address", "partner_1_share", "partner_2_name", "partner_2_address", "partner_2_share", "commencement_date", "capital_contribution_1", "capital_contribution_2"], "applicable_law": "Indian Partnership Act, 1932"},
    "general_poa": {"id": "general_poa", "name": "General Power of Attorney", "category": "Legal Documents", "description": "Authorization to act on behalf in all legal and financial matters", "fields": ["principal_name", "principal_address", "agent_name", "agent_address", "relationship", "scope_of_authority", "effective_date"], "applicable_law": "Powers of Attorney Act, 1882"},
    "special_poa": {"id": "special_poa", "name": "Specific Power of Attorney", "category": "Legal Documents", "description": "Limited authorization for a specific transaction or purpose", "fields": ["principal_name", "principal_address", "agent_name", "agent_address", "specific_purpose", "property_details", "effective_date", "expiry_date"], "applicable_law": "Powers of Attorney Act, 1882"},
    "affidavit_general": {"id": "affidavit_general", "name": "Affidavit (General)", "category": "Legal Documents", "description": "Sworn statement for various legal and administrative purposes", "fields": ["deponent_name", "deponent_address", "deponent_age", "deponent_occupation", "statement_purpose", "facts_to_state"], "applicable_law": "Oaths Act, 1969"},
    "bail_application": {"id": "bail_application", "name": "Bail Application (Regular)", "category": "Court Filings", "description": "Application for bail under Section 437/439 CrPC", "fields": ["accused_name", "accused_address", "fir_number", "fir_date", "police_station", "sections_charged", "court_name", "arrest_date", "grounds_for_bail"], "applicable_law": "Sections 437, 439, Code of Criminal Procedure, 1973"},
    "anticipatory_bail": {"id": "anticipatory_bail", "name": "Anticipatory Bail Application", "category": "Court Filings", "description": "Application for anticipatory bail under Section 438 CrPC", "fields": ["applicant_name", "applicant_address", "fir_number_if_any", "police_station", "sections_apprehended", "high_court_name", "grounds_for_anticipatory_bail"], "applicable_law": "Section 438, Code of Criminal Procedure, 1973"},
    "writ_habeas_corpus": {"id": "writ_habeas_corpus", "name": "Writ Petition - Habeas Corpus", "category": "Court Filings", "description": "Writ petition for release of unlawfully detained person", "fields": ["petitioner_name", "petitioner_address", "detenu_name", "detenu_relationship", "detaining_authority", "detention_date", "detention_place", "grounds"], "applicable_law": "Article 32 / Article 226, Constitution of India"},
    "writ_mandamus": {"id": "writ_mandamus", "name": "Writ Petition - Mandamus", "category": "Court Filings", "description": "Petition to compel a public authority to perform its duty", "fields": ["petitioner_name", "petitioner_address", "respondent_authority", "duty_to_be_performed", "prior_representations_made", "grounds", "relief_sought"], "applicable_law": "Article 32 / Article 226, Constitution of India"},
    "pil": {"id": "pil", "name": "Public Interest Litigation (PIL)", "category": "Court Filings", "description": "PIL petition to address public interest issues", "fields": ["petitioner_name", "petitioner_address", "respondents", "public_interest_issue", "facts", "grounds", "relief_sought", "prayer"], "applicable_law": "Article 32 (Supreme Court) / Article 226 (High Court), Constitution of India"},
    "divorce_mutual": {"id": "divorce_mutual", "name": "Divorce Petition (Mutual Consent)", "category": "Family Law", "description": "Joint petition for divorce by mutual consent", "fields": ["husband_name", "husband_address", "wife_name", "wife_address", "marriage_date", "marriage_place", "separation_date", "children_details", "alimony_amount", "child_custody_arrangement"], "applicable_law": "Section 13B, Hindu Marriage Act, 1955"},
    "divorce_contested": {"id": "divorce_contested", "name": "Divorce Petition (Contested)", "category": "Family Law", "description": "Petition for dissolution of marriage on specified grounds", "fields": ["petitioner_name", "petitioner_address", "respondent_name", "respondent_address", "marriage_date", "marriage_place", "ground_for_divorce", "specific_facts", "relief_sought"], "applicable_law": "Section 13, Hindu Marriage Act, 1955"},
    "child_custody": {"id": "child_custody", "name": "Child Custody Application", "category": "Family Law", "description": "Application for custody and guardianship of minor children", "fields": ["applicant_name", "applicant_address", "respondent_name", "child_name", "child_age", "custody_type", "grounds", "financial_capability"], "applicable_law": "Guardians and Wards Act, 1890"},
    "consumer_complaint": {"id": "consumer_complaint", "name": "Consumer Complaint (NCDRC/SCDRC)", "category": "Consumer", "description": "Complaint before Consumer Dispute Redressal Commission", "fields": ["complainant_name", "complainant_address", "opposite_party_name", "opposite_party_address", "goods_or_service", "purchase_date", "amount_paid", "deficiency_description", "relief_sought", "compensation_claimed"], "applicable_law": "Consumer Protection Act, 2019"},
    "rti_application": {"id": "rti_application", "name": "RTI Application", "category": "Consumer", "description": "Application for information under Right to Information Act", "fields": ["applicant_name", "applicant_address", "pio_designation", "public_authority_name", "public_authority_address", "information_sought", "time_period"], "applicable_law": "Right to Information Act, 2005"},
    "fir_complaint": {"id": "fir_complaint", "name": "FIR Complaint Letter", "category": "Criminal", "description": "Complaint letter to police for registration of FIR", "fields": ["complainant_name", "complainant_address", "police_station", "incident_date", "incident_place", "incident_description", "accused_details", "witnesses", "relief_sought"], "applicable_law": "Section 154, Code of Criminal Procedure, 1973"},
    "vakalatnama": {"id": "vakalatnama", "name": "Vakalatnama", "category": "Legal Documents", "description": "Authorization for an advocate to represent in court", "fields": ["client_name", "client_address", "advocate_name", "advocate_enrollment_number", "court_name", "case_title", "case_number_if_any"], "applicable_law": "Advocates Act, 1961; Order III CPC"},
    "will_testament": {"id": "will_testament", "name": "Will & Testament", "category": "Legal Documents", "description": "Last will and testament for distribution of assets", "fields": ["testator_name", "testator_address", "testator_age", "testator_occupation", "witness_1_name", "witness_1_address", "witness_2_name", "witness_2_address", "assets_description", "beneficiaries", "executor_name"], "applicable_law": "Indian Succession Act, 1925"},
    "rera_complaint": {"id": "rera_complaint", "name": "RERA Complaint", "category": "Property", "description": "Complaint before Real Estate Regulatory Authority", "fields": ["complainant_name", "complainant_address", "builder_name", "builder_address", "project_name", "rera_registration_number", "unit_number", "agreement_date", "amount_paid", "grievance_description", "relief_sought"], "applicable_law": "Real Estate (Regulation and Development) Act, 2016"},
    "labour_complaint": {"id": "labour_complaint", "name": "Labour Court Complaint", "category": "Labour", "description": "Complaint for illegal termination or labour rights violation", "fields": ["complainant_name", "complainant_address", "employer_name", "employer_address", "employment_start_date", "termination_date", "last_drawn_salary", "nature_of_grievance", "relief_sought"], "applicable_law": "Industrial Disputes Act, 1947"},
}

DOCUMENT_SYSTEM = """You are Lawgic AI, an expert Indian legal document drafter with 20 years of experience.
You create complete, legally sound documents using proper Indian legal language and format.
Documents should:
- Use formal legal language appropriate for Indian courts and authorities
- Include all standard clauses and protective provisions
- Be complete and ready to use (with placeholders like [NOTARY SEAL] where needed)
- Reference specific applicable Indian law sections
- Follow standard Indian legal document formatting
Always generate the COMPLETE document - never truncate or summarize."""


async def document_generation_node(state: AgentState, db=None) -> AgentState:
    logs = list(state.get("agent_logs", []))
    user_query = state.get("user_query", "")
    case_ctx = state.get("case_context", {})

    template_id = case_ctx.get("template_id", "")
    form_data = case_ctx.get("form_data", {})
    template = TEMPLATES.get(template_id)

    template_name = template["name"] if template else "Legal Document"
    applicable_law = template["applicable_law"] if template else "Indian law"

    logs.append(f"document_agent: Generating {template_name}")

    prompt = f"""Generate a complete, legally sound {template_name} for use in India.

Applicable Law: {applicable_law}

Details provided:
{json.dumps(form_data, indent=2)}

Additional context: {user_query}

Generate the COMPLETE document with proper heading, all parties, standard clauses, law references, signature blocks, and witness sections."""

    messages = [{"role": "user", "content": prompt}]
    try:
        document_text = await get_claude_response(messages, system=DOCUMENT_SYSTEM)
        logs.append(f"document_agent: Document generated ({len(document_text)} chars)")
        return {**state, "generated_document": document_text, "final_response": document_text, "confidence_score": 0.9, "agent_logs": logs}
    except Exception as e:
        logs.append(f"document_agent: Error - {str(e)}")
        return {**state, "final_response": f"Error generating document: {str(e)}", "agent_logs": logs}


def get_all_templates() -> list:
    return list(TEMPLATES.values())


def get_template(template_id: str) -> dict | None:
    return TEMPLATES.get(template_id)
