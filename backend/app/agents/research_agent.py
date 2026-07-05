from app.agents.state import AgentState
from app.services.claude import get_claude_response

KNOWLEDGE_BASE = [
    {
        "id": "ipc_302", "title": "IPC Section 302 - Murder", "type": "statute",
        "excerpt": "Punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "full_text": "Section 302, Indian Penal Code, 1860: Punishment for murder — Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "keywords": ["murder", "homicide", "death", "302", "ipc"],
    },
    {
        "id": "ipc_376", "title": "IPC Section 376 - Rape", "type": "statute",
        "excerpt": "Punishment for rape. Shall be punished with rigorous imprisonment for not less than 10 years, extendable to life imprisonment.",
        "full_text": "Section 376, IPC: Whoever commits rape shall be punished with rigorous imprisonment for a term not less than ten years, which may extend to imprisonment for life.",
        "keywords": ["rape", "sexual assault", "376", "ipc", "pocso"],
    },
    {
        "id": "ipc_420", "title": "IPC Section 420 - Cheating", "type": "statute",
        "excerpt": "Cheating and dishonestly inducing delivery of property. Punishment: imprisonment up to 7 years and fine.",
        "full_text": "Section 420, IPC: Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, shall be punished with imprisonment of either description for a term up to 7 years, and also liable to fine.",
        "keywords": ["cheating", "fraud", "420", "ipc", "property", "dishonest"],
    },
    {
        "id": "ipc_498a", "title": "IPC Section 498A - Cruelty by Husband", "type": "statute",
        "excerpt": "Husband or relative of husband of a woman subjecting her to cruelty. Imprisonment up to 3 years and fine.",
        "full_text": "Section 498A, IPC: Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for up to 3 years and fine. Cognizable, non-bailable, triable by Magistrate.",
        "keywords": ["498a", "cruelty", "domestic violence", "husband", "dowry", "matrimonial"],
    },
    {
        "id": "ni_act_138", "title": "Section 138 NI Act - Cheque Bounce", "type": "statute",
        "excerpt": "Dishonour of cheque for insufficiency of funds. Punishable with imprisonment up to 2 years, or fine up to twice the cheque amount, or both.",
        "full_text": "Section 138, Negotiable Instruments Act, 1881: Where any cheque is dishonoured by the bank due to insufficiency of funds or if it exceeds the amount arranged to be paid from that account, the drawer commits an offence punishable with imprisonment up to 2 years, or fine up to twice the amount of the cheque, or both.",
        "keywords": ["cheque bounce", "dishonour", "138", "negotiable instruments", "bank", "insufficiency"],
    },
    {
        "id": "consumer_2019", "title": "Consumer Protection Act, 2019", "type": "statute",
        "excerpt": "Provides for protection of consumers from unfair trade practices. Establishes NCDRC, SCDRC, DCDRC for consumer dispute redressal.",
        "full_text": "The Consumer Protection Act, 2019 provides a three-tier quasi-judicial consumer dispute redressal mechanism: District Consumer Disputes Redressal Commission (DCDRC) for claims up to ₹1 crore; State Consumer Disputes Redressal Commission (SCDRC) for ₹1-10 crore; National Consumer Disputes Redressal Commission (NCDRC) for above ₹10 crore.",
        "keywords": ["consumer", "consumer protection", "NCDRC", "SCDRC", "unfair trade", "deficiency of service"],
    },
    {
        "id": "rti_2005", "title": "Right to Information Act, 2005", "type": "statute",
        "excerpt": "Citizens have right to access information from public authorities. Response required within 30 days (48 hours if life/liberty at stake).",
        "full_text": "The RTI Act, 2005 grants citizens the right to request information from any public authority. The Public Information Officer (PIO) must respond within 30 days. First appeal lies with the Appellate Authority; second appeal to State/Central Information Commission. Fee: ₹10 per application.",
        "keywords": ["RTI", "right to information", "transparency", "public authority", "information", "government"],
    },
    {
        "id": "rera_2016", "title": "Real Estate (Regulation and Development) Act, 2016 - RERA", "type": "statute",
        "excerpt": "Regulates real estate sector. Developers must register projects; buyers can claim refund and compensation for delay.",
        "full_text": "RERA, 2016 mandates registration of real estate projects and agents. Buyers are entitled to: timely possession, refund with interest on delay, compensation for defects, and access to project information. Complaints can be filed before the State RERA Authority.",
        "keywords": ["RERA", "real estate", "builder", "property", "possession delay", "refund", "homebuyer"],
    },
    {
        "id": "domestic_violence_2005", "title": "Protection of Women from Domestic Violence Act, 2005", "type": "statute",
        "excerpt": "Provides protection and remedy to women victims of domestic violence. Includes physical, emotional, sexual, economic abuse.",
        "full_text": "The DV Act, 2005 defines domestic violence broadly to include physical, sexual, verbal, emotional, and economic abuse. Reliefs available: Protection Orders, Residence Orders, Monetary Relief, Custody Orders, Compensation Orders. Application to Magistrate; Domestic Incident Report by Protection Officer.",
        "keywords": ["domestic violence", "DV Act", "protection order", "women rights", "abuse", "restraining order"],
    },
    {
        "id": "ibc_2016", "title": "Insolvency and Bankruptcy Code, 2016 (IBC)", "type": "statute",
        "excerpt": "Consolidated framework for insolvency resolution of companies, LLPs and individuals. CIRP initiated before NCLT.",
        "full_text": "IBC, 2016 provides time-bound (330 days) Corporate Insolvency Resolution Process (CIRP) before NCLT. Financial/Operational creditors can file application. Resolution Professional manages the process. If no resolution plan approved, liquidation is ordered.",
        "keywords": ["IBC", "insolvency", "bankruptcy", "CIRP", "NCLT", "liquidation", "NPA", "creditor"],
    },
    {
        "id": "vishakha_posh", "title": "POSH Act - Sexual Harassment at Workplace", "type": "statute",
        "excerpt": "Prevention, Prohibition and Redressal of Sexual Harassment of Women at Workplace Act, 2013. Internal Complaints Committee mandatory for 10+ employee organisations.",
        "full_text": "The POSH Act, 2013 mandates every employer with 10+ employees to constitute an Internal Complaints Committee (ICC). Complaints must be filed within 3 months. Enquiry to be completed in 90 days. Punishment: fine up to ₹50,000, service termination.",
        "keywords": ["POSH", "sexual harassment", "workplace", "ICC", "women", "MeToo"],
    },
    {
        "id": "hindu_marriage_13b", "title": "Section 13B Hindu Marriage Act - Mutual Consent Divorce", "type": "statute",
        "excerpt": "Divorce by mutual consent available after 1 year of separation. Second motion after 6-18 months cooling period.",
        "full_text": "Section 13B, Hindu Marriage Act, 1955: Both parties can present a petition for divorce by mutual consent after living separately for 1 year. After 6-18 months, they may move the second motion. The Supreme Court in Amardeep Singh v. Harveen Kaur (2017) held that the 6-month cooling period can be waived.",
        "keywords": ["mutual consent divorce", "13B", "Hindu Marriage Act", "separation", "divorce"],
    },
    {
        "id": "article_21", "title": "Article 21 - Right to Life and Personal Liberty", "type": "statute",
        "excerpt": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
        "full_text": "Article 21, Constitution of India: No person shall be deprived of his life or personal liberty except according to procedure established by law. The Supreme Court has expanded this to include right to livelihood, health, education, shelter, privacy (Puttaswamy judgment), and dignity.",
        "keywords": ["article 21", "right to life", "personal liberty", "constitution", "fundamental rights", "privacy"],
    },
    {
        "id": "olx_v_facebook", "title": "Landmark: Shreya Singhal v. Union of India (2015)", "type": "case",
        "excerpt": "Supreme Court struck down Section 66A of IT Act as unconstitutional for being vague and overbroad, violating Article 19(1)(a).",
        "full_text": "Shreya Singhal v. Union of India (2015) 5 SCC 1: The Supreme Court declared Section 66A of IT Act unconstitutional as it restricted free speech online with vague terms. This case established that online speech has the same protection as offline speech under Article 19(1)(a).",
        "keywords": ["66A", "IT Act", "internet", "free speech", "Shreya Singhal", "online"],
    },
    {
        "id": "maneka_gandhi", "title": "Landmark: Maneka Gandhi v. Union of India (1978)", "type": "case",
        "excerpt": "Supreme Court held that procedure under Article 21 must be fair, just, and reasonable. Expanded scope of Article 21 significantly.",
        "full_text": "Maneka Gandhi v. Union of India (1978) 1 SCC 248: The Supreme Court held that the procedure under Article 21 must be fair, just, and reasonable. This overruled A.K. Gopalan and established inter-relationship between Articles 14, 19, and 21.",
        "keywords": ["Article 21", "Maneka Gandhi", "fair procedure", "natural justice", "fundamental rights"],
    },
    {
        "id": "industrial_disputes", "title": "Industrial Disputes Act, 1947", "type": "statute",
        "excerpt": "Governs industrial relations, strikes, lockouts, layoffs, retrenchment. Chapter VB requires government permission for layoffs in establishments with 100+ workers.",
        "full_text": "The Industrial Disputes Act, 1947 provides for investigation and settlement of industrial disputes. Section 25F: retrenchment compensation (15 days' wages per year of service). Chapter VB: establishments with 100+ workers require government permission for retrenchment/closure. Labour Court/Industrial Tribunal for disputes.",
        "keywords": ["labour law", "retrenchment", "termination", "industrial dispute", "workman", "compensation"],
    },
    {
        "id": "crpc_41a", "title": "CrPC Section 41A - Notice to Appear", "type": "statute",
        "excerpt": "Police must issue Section 41A notice before arrest in cases carrying less than 7 years imprisonment. Arnesh Kumar judgment mandates this.",
        "full_text": "Section 41A, CrPC (post-2009 amendment): The police officer shall, in all cases where arrest of a person is not required, issue a notice directing the person to appear before him or at such other place as specified. Non-compliance is then grounds for arrest. Arnesh Kumar v. State of Bihar (2014) mandated this in all Section 498A cases.",
        "keywords": ["41A", "notice", "arrest", "police", "Arnesh Kumar", "498A", "bail"],
    },
    {
        "id": "companies_act_248", "title": "Companies Act, 2013 - Section 248 Strike Off", "type": "statute",
        "excerpt": "Registrar can strike off defunct companies. Directors can apply for voluntary strike-off if no liabilities exist.",
        "full_text": "Section 248, Companies Act 2013: The Registrar of Companies may strike off company name if not carrying on business for 2 consecutive years. Directors can apply for voluntary strike-off under Section 248(2) using Form STK-2 after extinguishing all liabilities.",
        "keywords": ["company", "strike off", "closure", "ROC", "defunct", "Companies Act"],
    },
    {
        "id": "gst_registration", "title": "GST Registration and Compliance", "type": "statute",
        "excerpt": "Businesses with turnover > ₹40 lakhs (goods) or ₹20 lakhs (services) must register under GST. Monthly/quarterly filing mandatory.",
        "full_text": "The Goods and Services Tax (GST) applies to supply of goods and services in India. Mandatory registration threshold: ₹40 lakh for goods, ₹20 lakh for services (₹10 lakh in special category states). GSTR-1 (outward supplies), GSTR-3B (summary return). Input tax credit available on business purchases.",
        "keywords": ["GST", "tax", "registration", "GSTR", "input tax credit", "business", "turnover"],
    },
    {
        "id": "specific_relief_10", "title": "Specific Relief Act - Specific Performance", "type": "statute",
        "excerpt": "Courts may order specific performance of contracts for immovable property. Post-2018 amendment made specific performance a rule, not discretion.",
        "full_text": "Specific Relief Act, 1963 (amended 2018): Section 10 - specific performance of contracts for immovable property is now mandatory (not discretionary) unless breach occurred due to the plaintiff's own conduct. Injunctions available under Section 37-42.",
        "keywords": ["specific performance", "contract", "property", "specific relief", "immovable property"],
    },
]

RESEARCH_SYSTEM = """You are Lawgic AI, an expert in Indian law research with access to IPC, CrPC, CPC, Consumer Protection Act, RTI Act, RERA, Companies Act, IBC, family law, and constitutional law.

When answering research queries:
1. Identify the most relevant statutes and sections
2. Cite landmark Supreme Court and High Court judgments with year
3. Explain practical implications for the user
4. Be precise about section numbers and case citations
5. Note any recent amendments or landmark judgments"""


async def legal_research_node(state: AgentState, db=None) -> AgentState:
    """Search legal knowledge base and provide comprehensive research results."""
    logs = list(state.get("agent_logs", []))
    query = state.get("user_query", "")
    logs.append(f"research_agent: Searching for '{query}'")

    # Simple keyword search in knowledge base
    query_lower = query.lower()
    results = []
    for item in KNOWLEDGE_BASE:
        score = sum(1 for kw in item["keywords"] if kw in query_lower)
        if score > 0:
            results.append({**item, "relevance_score": score})

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    top_results = results[:5]

    # Build context from results
    kb_context = ""
    if top_results:
        kb_context = "\n\nRelevant knowledge base entries:\n"
        for r in top_results:
            kb_context += f"\n- {r['title']}: {r['excerpt']}"

    prompt = f"""Research query: {query}{kb_context}

Provide a comprehensive legal research response covering:
1. Most relevant Indian laws and sections
2. Key landmark cases with citations
3. Practical guidance for this situation
4. Any important recent developments
5. Recommended next steps"""

    messages = [{"role": "user", "content": prompt}]
    try:
        ai_summary = await get_claude_response(messages, system=RESEARCH_SYSTEM)

        # Format results for response
        formatted_results = []
        for r in top_results:
            formatted_results.append({
                "title": r["title"],
                "type": r["type"],
                "excerpt": r["excerpt"],
                "relevance_score": r["relevance_score"] / 5.0,
            })

        logs.append(f"research_agent: Found {len(formatted_results)} relevant entries")
        return {
            **state,
            "research_results": formatted_results,
            "final_response": ai_summary,
            "confidence_score": 0.85,
            "agent_logs": logs,
        }
    except Exception as e:
        logs.append(f"research_agent: Error - {str(e)}")
        return {**state, "final_response": f"Research error: {str(e)}", "agent_logs": logs}


def search_knowledge_base(query: str, category: str = None) -> list:
    """Direct knowledge base search for API endpoint."""
    query_lower = query.lower()
    results = []
    for item in KNOWLEDGE_BASE:
        if category and item["type"] != category:
            continue
        score = sum(1 for kw in item["keywords"] if kw in query_lower)
        if score > 0:
            results.append({**item, "relevance_score": round(score / 5.0, 2)})
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:10]
