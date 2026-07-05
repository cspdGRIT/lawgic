from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


COURSES = [
    {
        "id": "know-your-rights",
        "title": "Know Your Legal Rights in India",
        "level": "Beginner",
        "description": "Understand your fundamental rights under the Indian Constitution and how to exercise them in everyday situations.",
        "duration_hours": 3,
        "lessons_count": 6,
        "category": "Fundamental Rights",
        "image_emoji": "⚖️",
        "lessons": [
            {"id": 1, "title": "Introduction to Fundamental Rights", "content": "The Indian Constitution guarantees 6 fundamental rights to all citizens under Articles 12-35. These rights are justiciable, meaning you can approach courts if they are violated.\n\n**Right to Equality (Art 14-18)**: No discrimination on grounds of religion, race, caste, sex, or place of birth. Includes equal opportunity in public employment.\n\n**Right to Freedom (Art 19-22)**: Includes freedom of speech, assembly, movement, residence, and profession. Right to life and personal liberty under Article 21 is the most expansive fundamental right.\n\n**Right against Exploitation (Art 23-24)**: Prohibition of human trafficking, forced labour, and child labour in hazardous occupations.\n\n**Right to Freedom of Religion (Art 25-28)**: Right to profess, practice, and propagate religion.\n\n**Cultural and Educational Rights (Art 29-30)**: Minorities can conserve their culture and establish educational institutions.\n\n**Right to Constitutional Remedies (Art 32)**: Dr Ambedkar called this the 'heart and soul' of the Constitution. You can directly approach the Supreme Court for enforcement of fundamental rights.", "duration_mins": 25},
            {"id": 2, "title": "Right to Life - Article 21", "content": "Article 21 is the broadest and most expansive fundamental right: 'No person shall be deprived of his life or personal liberty except according to procedure established by law.'\n\nThe Supreme Court has expanded this to include:\n- Right to livelihood\n- Right to health\n- Right to education\n- Right to shelter\n- Right to privacy (Puttaswamy judgment, 2017)\n- Right to dignity\n- Right to free legal aid\n- Right against solitary confinement\n- Right to bail\n\n**Maneka Gandhi v. Union of India (1978)**: The procedure must be fair, just, and reasonable. Arbitrary laws violating Article 21 are unconstitutional.\n\n**Practical application**: If you are arrested, you have the right to be informed of grounds of arrest, right to legal representation, right to be produced before magistrate within 24 hours.", "duration_mins": 20},
            {"id": 3, "title": "Rights of an Arrested Person", "content": "When you are arrested in India, you have these legal rights:\n\n**Under Section 50 CrPC**: You must be informed of the grounds of your arrest immediately.\n\n**Under Section 41A CrPC**: Police must issue notice (Section 41A notice) before arresting you in cases carrying less than 7 years imprisonment. The Arnesh Kumar judgment (2014) is landmark.\n\n**Under Section 57 CrPC**: You cannot be detained for more than 24 hours without being produced before a magistrate.\n\n**Under Article 22**: You have the right to consult and be defended by a legal practitioner of your choice.\n\n**Under Section 303 CrPC**: You are entitled to be defended by a pleader of your choice.\n\n**Under Article 22(2)**: You must be produced before the nearest magistrate within 24 hours of arrest (excluding travel time).\n\n**Free Legal Aid**: Under Section 304 CrPC, if you cannot afford a lawyer, the court must provide one at state expense.", "duration_mins": 20},
            {"id": 4, "title": "Consumer Rights", "content": "The Consumer Protection Act, 2019 provides comprehensive rights to consumers in India.\n\n**6 Consumer Rights**:\n1. Right to Safety\n2. Right to be Informed\n3. Right to Choose\n4. Right to be Heard\n5. Right to Seek Redressal\n6. Right to Consumer Education\n\n**Where to complain**:\n- DCDRC (District Commission): Claims up to ₹1 crore\n- SCDRC (State Commission): ₹1-10 crore\n- NCDRC (National Commission): Above ₹10 crore\n- Centralized: nationalconsumerhelpline.gov.in, Toll-free: 1800-11-4000\n\n**E-commerce**: Special provisions for online purchases. You can complain against Amazon, Flipkart, etc.\n\n**Time Limit**: File complaint within 2 years of cause of action.\n\n**What you can claim**: Refund, replacement, compensation, and punitive damages.", "duration_mins": 25},
            {"id": 5, "title": "Property Rights in India", "content": "Understanding property rights is essential for every Indian citizen.\n\n**Types of Property Rights**:\n- Freehold: Complete ownership\n- Leasehold: Right to use for specific period\n- Joint Property: Co-ownership\n- Ancestral Property: Inherited through male lineage (Hindu law)\n\n**Hindu Succession Act, 2005 Amendment**: Daughters now have equal coparcenary rights in ancestral property.\n\n**Documents for Property**:\n- Sale Deed (registered)\n- Encumbrance Certificate\n- Khata/Mutation Records\n- Property Tax Receipts\n\n**RERA Protection**: If builder delays possession, you can:\n1. Seek refund with interest\n2. Continue with compensation @ SBI lending rate + 2%\n3. File complaint before State RERA Authority\n\n**Tenant Rights**: Eviction only through proper legal process. You cannot be evicted without notice and court order.", "duration_mins": 20},
            {"id": 6, "title": "RTI - Your Transparency Tool", "content": "The Right to Information Act, 2005 is one of the most powerful tools for citizens.\n\n**What you can ask**:\n- Why your application was rejected\n- Status of your complaint\n- Details of government contracts\n- Information about public servants\n- Details of schemes and their beneficiaries\n\n**How to file RTI**:\n1. Write to Public Information Officer (PIO) of the concerned department\n2. Pay ₹10 application fee (BPL applicants: free)\n3. Response within 30 days (48 hours if life/liberty at stake)\n\n**If unsatisfied**:\n- First Appeal: Within 30 days to First Appellate Authority\n- Second Appeal: Within 90 days to State/Central Information Commission\n\n**Online RTI**: rtionline.gov.in for central government\n\n**Exemptions**: Cabinet notes, security/intelligence, personal information of third parties unless public interest.", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Which Article of the Indian Constitution guarantees Right to Life and Personal Liberty?", "options": ["Article 14", "Article 19", "Article 21", "Article 32"], "correct": 2},
            {"question": "Within how many hours must an arrested person be produced before a magistrate?", "options": ["12 hours", "24 hours", "48 hours", "72 hours"], "correct": 1},
            {"question": "What is the filing fee for an RTI application?", "options": ["₹5", "₹10", "₹20", "₹50"], "correct": 1},
            {"question": "The Consumer Protection Act, 2019 allows complaints up to what amount before the National Commission?", "options": ["Above ₹1 crore", "Above ₹5 crore", "Above ₹10 crore", "Above ₹20 crore"], "correct": 2},
            {"question": "Under the 2005 amendment to Hindu Succession Act, daughters have what rights in ancestral property?", "options": ["No rights", "Rights only after father's death", "Equal coparcenary rights", "Rights only if unmarried"], "correct": 2},
        ],
    },
    {
        "id": "cheque-bounce-law",
        "title": "Cheque Bounce Law - Section 138 NI Act",
        "level": "Intermediate",
        "description": "Master the law on dishonoured cheques - one of the most common legal disputes in India with over 4.5 million cases pending.",
        "duration_hours": 2,
        "lessons_count": 4,
        "category": "Criminal Law",
        "image_emoji": "🏦",
        "lessons": [
            {"id": 1, "title": "What is Section 138 NI Act?", "content": "Section 138 of the Negotiable Instruments Act, 1881 makes dishonour of cheques a criminal offence.\n\n**Elements of the offence**:\n1. There must be a legally enforceable debt or liability\n2. The drawer must have issued a cheque for discharge of that debt\n3. The cheque must be dishonoured due to insufficient funds OR amount exceeding the arranged payment\n4. The payee must send a legal notice within 30 days of dishonour\n5. The drawer must fail to pay within 15 days of receiving notice\n\n**Punishment**: Imprisonment up to 2 years, OR fine up to twice the cheque amount, OR both.\n\n**Important**: This is both a criminal and civil remedy. You can also file civil suit for recovery simultaneously.", "duration_mins": 20},
            {"id": 2, "title": "Procedure: Notice and Filing", "content": "**Step 1: Get Cheque Return Memo** from bank within 30 days of dishonour.\n\n**Step 2: Send Legal Notice** within 30 days of cheque return, by registered post/courier:\n- Must specifically mention dishonour, date, cheque number, amount\n- Demand payment within 15 days\n\n**Step 3: Wait 15 days** for payment.\n\n**Step 4: File complaint** within 30 days of expiry of 15-day notice period, before Judicial Magistrate First Class (JMFC) in whose jurisdiction:\n- Cheque was issued, OR\n- Cheque was presented, OR\n- Payment was to be made\n\n**Documents needed**: Original cheque (or copy), bank return memo, copy of legal notice, postal receipt/acknowledgement.", "duration_mins": 25},
            {"id": 3, "title": "Supreme Court Judgments", "content": "Key Supreme Court judgments on Section 138:\n\n**Dashrath Rupsingh Rathod v. State of Maharashtra (2014)**: Complaint must be filed where cheque is delivered for collection (usually payee's bank), NOT where cheque bounces.\n\n**MSR Leathers v. S. Palaniappan (2013)**: Multiple complaints for same cheque not maintainable.\n\n**Meters and Instruments v. Kanchan Mehta (2017)**: Court can allow one-time settlement; Section 138 is quasi-criminal.\n\n**Makwana Mangaldas Tulsidas v. State of Gujarat (2019)**: Issuance of notice is mandatory, defective notice makes the complaint non-maintainable.\n\n**Recent**: Cognizance can be taken even before accused is summoned. Interim compensation up to 20% of cheque amount can be ordered.", "duration_mins": 20},
            {"id": 4, "title": "Defences Available", "content": "Defences for the drawer (accused):\n\n1. **No legally enforceable debt**: Cheque was given as gift, security, or for time-barred debt\n2. **Cheque was stolen/forged**: Drawer's signature forged\n3. **Stop payment before dishonour**: If payment stopped before presentation for valid reason\n4. **Improper notice**: Notice not sent correctly or within 30 days\n5. **Time-barred complaint**: Filed after limitation period\n6. **No debt subsisting**: Debt was already paid\n\n**Key**: The burden of proof shifts to drawer to prove no debt existed once complainant proves basic facts.\n\n**Compounding**: Section 147 allows compounding (settlement) at any stage, even during appeal, with court permission.", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Within how many days of cheque dishonour must you send the legal notice?", "options": ["15 days", "30 days", "45 days", "60 days"], "correct": 1},
            {"question": "What is the maximum punishment under Section 138 NI Act?", "options": ["6 months", "1 year", "2 years", "3 years"], "correct": 2},
            {"question": "Where should you file the complaint under Section 138?", "options": ["Where cheque was drawn", "Where payee's bank is located", "Where drawer lives", "Any court in India"], "correct": 1},
            {"question": "Within how many days must the drawer pay after receiving legal notice?", "options": ["7 days", "10 days", "15 days", "30 days"], "correct": 2},
            {"question": "Can a Section 138 case be settled/compounded?", "options": ["No, it cannot be settled", "Yes, at any stage with court permission", "Only before filing complaint", "Only with government permission"], "correct": 1},
        ],
    },
    {
        "id": "consumer-rights",
        "title": "Consumer Rights & RERA",
        "level": "Beginner",
        "description": "Fight back against unfair trade practices, defective products, and builder delays using the Consumer Protection Act 2019 and RERA.",
        "duration_hours": 2.5,
        "lessons_count": 5,
        "category": "Consumer Rights",
        "image_emoji": "🛒",
        "lessons": [
            {"id": 1, "title": "Consumer Protection Act 2019", "content": "The Consumer Protection Act, 2019 replaced the 1986 Act with stronger protections.\n\n**Key improvements in 2019 Act**:\n- E-commerce included\n- Product liability provisions\n- Unfair contracts covered\n- Simplified complaint process\n- Mediation as alternative\n\n**Who is a consumer?**: Any person who buys goods or hires services for personal use (not for commercial resale).\n\n**What is deficiency?**: Any fault in service that falls short of standard quality/performance.\n\n**Jurisdiction**: DCDRC (up to ₹1 crore), SCDRC (₹1-10 crore), NCDRC (above ₹10 crore).", "duration_mins": 20},
            {"id": 2, "title": "How to File a Consumer Complaint", "content": "Filing a consumer complaint is simpler than you think.\n\n**Online**: edaakhil.nic.in - file complaint from home!\n\n**Steps**:\n1. Register on eDaakhil portal\n2. Fill complaint form with details\n3. Upload documents (bill, warranty, correspondence)\n4. Pay court fee (varies by claim amount)\n5. Complaint is listed for hearing\n\n**Documents needed**:\n- Purchase invoice/receipt\n- Warranty card\n- Correspondence with company\n- Expert report (if product defect)\n- Medical bills (if health affected)\n\n**Reliefs available**:\n- Replacement of defective product\n- Refund with interest\n- Compensation for loss/injury\n- Punitive damages\n- Removal of deficiency in service", "duration_mins": 25},
            {"id": 3, "title": "RERA - Builder Accountability", "content": "RERA (Real Estate Regulation and Development Act, 2016) protects homebuyers.\n\n**Builder's obligations**:\n- Register project before selling\n- Advertise only registered projects\n- Deliver on committed date\n- Maintain escrow account (70% of buyer money)\n- Fix structural defects within 5 years\n\n**Your rights under RERA**:\n- Access project information on RERA website\n- Refund with interest (@ SBI lending rate + 2%) on delay\n- Compensation without having to give up project\n- Complain to RERA Authority\n\n**Compensation formula**: If builder delays by 6 months, you get interest on amount paid for 6 months.", "duration_mins": 25},
            {"id": 4, "title": "Product Liability", "content": "The 2019 Act introduces product liability - manufacturers and sellers are responsible for defective products.\n\n**Who can be held liable**:\n- Manufacturer\n- Product service provider  \n- Product seller (including online marketplaces in some cases)\n\n**Grounds for claim**:\n- Manufacturing defect\n- Design defect\n- Inadequate warnings/instructions\n- False claims about product\n\n**No need to prove negligence**: Unlike tort law, product liability under 2019 Act is strict liability.\n\n**Limitation**: No liability if product tampered, not used as intended, or defect occurred after product left manufacturer.", "duration_mins": 20},
            {"id": 5, "title": "National Consumer Helpline", "content": "Before filing a case, try these quick remedies:\n\n**National Consumer Helpline**: 1800-11-4000 (Toll Free) or 14404\nWebsite: consumerhelpline.gov.in\n\n**INGRAM (Integrated Grievance Address Monitoring System)**: consumerhelpline.gov.in - companies are expected to respond within 30 days.\n\n**RBI Banking Ombudsman**: For bank complaints\n**IRDAI Insurance Ombudsman**: For insurance complaints\n**TRAI**: For telecom complaints\n**SEBI SCORES**: For stock market complaints\n\n**Amazon/Flipkart disputes**: File on eDaakhil. Courts have held e-commerce platforms as service providers.", "duration_mins": 10},
        ],
        "quiz": [
            {"question": "What is the maximum claim amount before DCDRC (District Consumer Commission)?", "options": ["₹20 lakhs", "₹50 lakhs", "₹1 crore", "₹5 crore"], "correct": 2},
            {"question": "Which website allows you to file consumer complaints online?", "options": ["consumercomplaints.in", "edaakhil.nic.in", "ncdrc.gov.in", "consumercourt.gov.in"], "correct": 1},
            {"question": "Under RERA, what interest does a builder pay for delayed possession?", "options": ["6% per annum", "SBI lending rate", "SBI lending rate + 2%", "12% per annum"], "correct": 2},
            {"question": "What is the National Consumer Helpline number?", "options": ["1800-11-3000", "1800-11-4000", "14400", "14404"], "correct": 1},
            {"question": "Product liability under Consumer Protection Act 2019 requires proof of:", "options": ["Negligence by manufacturer", "Intentional defect", "No proof of negligence needed (strict liability)", "Criminal intent"], "correct": 2},
        ],
    },
    {
        "id": "startup-legal",
        "title": "Legal Essentials for Startups",
        "level": "Advanced",
        "description": "Everything founders need to know about company formation, equity, IP protection, compliance, and funding documentation in India.",
        "duration_hours": 5,
        "lessons_count": 6,
        "category": "Corporate Law",
        "image_emoji": "🚀",
        "lessons": [
            {"id": 1, "title": "Choosing the Right Business Structure", "content": "**Sole Proprietorship**: Easiest to start, no separate legal entity, full personal liability.\n\n**Partnership Firm**: 2-20 partners (banking: 2-10), registered under Indian Partnership Act 1932. Partners have unlimited liability.\n\n**LLP (Limited Liability Partnership)**: Best for service firms. Separate legal entity, limited liability for partners, flexible management, pass-through taxation.\n\n**Private Limited Company**: Best for startups. Separate legal entity, limited liability, can raise equity, ESOP possible, FDI allowed.\n\n**OPC (One Person Company)**: New structure for solo founders. Limited liability, only Indian citizen can be promoter.\n\n**Recommendation for VC-backed startups**: Private Limited Company incorporated in India or Singapore/Delaware for global fundraising.", "duration_mins": 25},
            {"id": 2, "title": "IP Protection for Startups", "content": "**Trademarks**: Protect your brand name and logo. Register at ipindia.gov.in. Time: 12-18 months. Classes: 45 classes based on goods/services.\n\n**Patents**: Protect inventions. File provisional specification first (12 months to file complete). Novel + inventive step + industrial application.\n\n**Copyright**: Automatic on creation. Register at copyright.gov.in for evidence of ownership. Software, content, creative works.\n\n**Trade Secrets**: Protect through NDAs, employment agreements, non-compete clauses. No registration required.\n\n**Domain & Social Media**: Register brand across platforms early.\n\n**Key**: File trademark BEFORE launch. Section 29 infringement if someone uses similar mark for similar goods.", "duration_mins": 30},
            {"id": 3, "title": "Founders' Agreement & ESOP", "content": "**Founders' Agreement must cover**:\n- Equity split and vesting schedule (typically 4 years, 1-year cliff)\n- IP assignment to company\n- Decision-making process\n- Role and responsibilities\n- Non-compete and non-solicitation\n- What happens if a founder leaves\n\n**ESOP Pool**: Typically 10-20% for team. Create ESOP scheme under Companies Act. Options vest over 4 years. Exercise price set at face value or market price.\n\n**SHA (Shareholders' Agreement)**: Critical for investor-founder relationship. Covers anti-dilution, pro-rata rights, drag-along, tag-along, information rights, board composition.\n\n**Watch out**: Vesting must be waterproof. Cliff and vesting protects remaining founders if one leaves early.", "duration_mins": 30},
            {"id": 4, "title": "Fundraising Documentation", "content": "**Term Sheet**: Non-binding document outlining investment terms. Key terms: valuation, liquidation preference, anti-dilution, board seat, information rights.\n\n**SHA (Shareholders' Agreement)**: Binding. Governs rights between investors and founders.\n\n**SSA (Share Subscription Agreement)**: Legal document for shares being issued to investor.\n\n**SAFE (Simple Agreement for Future Equity)**: Popular for early-stage. No valuation needed immediately. Converts at next priced round.\n\n**Compulsorily Convertible Debentures (CCDs)**: Popular for FDI compliance as CCDs don't count as debt for FEMA purposes.\n\n**FEMA Compliance**: Mandatory for foreign investment. FCGPR filing with RBI within 30 days of receiving foreign investment.", "duration_mins": 25},
            {"id": 5, "title": "Employment Law for Startups", "content": "**Key Compliance**:\n- PF (Provident Fund): Mandatory for 20+ employees. 12% employer + 12% employee contribution\n- ESI: For employees earning <₹21,000/month. 3.25% employer + 0.75% employee\n- Professional Tax: State-specific, up to ₹2,500/year\n- TDS on Salaries: Section 192\n\n**Employment Agreement must cover**:\n- Confidentiality\n- IP assignment\n- Non-solicitation\n- Notice period\n- ESOP terms\n\n**Termination**: Follow proper procedure. Pay gratuity (5+ years). No-fault termination requires notice.\n\n**Contractors vs Employees**: Misclassification risk. Real test: control over work method, exclusivity, integration into business.", "duration_mins": 25},
            {"id": 6, "title": "Regulatory Compliance", "content": "**Annual Filings (Private Limited)**:\n- AOC-4 (Financial Statements): Within 30 days of AGM\n- MGT-7 (Annual Return): Within 60 days of AGM\n- ADT-1 (Auditor Appointment): Within 15 days\n- DIN KYC: Annual director KYC\n\n**GST Compliance**:\n- Register if turnover > ₹20 lakh (services)\n- GSTR-1 monthly or quarterly\n- GSTR-3B monthly summary\n\n**Startup India Benefits**:\n- DPIIT Recognition: Self-certification of employment, labour laws\n- Tax exemption: 3 years tax holiday under Section 80-IAC\n- Easy winding up under IBC\n- ₹20 lakh seed grant available\n\n**Register at startupindia.gov.in** for these benefits.", "duration_mins": 25},
        ],
        "quiz": [
            {"question": "Which business structure is best for startups planning VC funding?", "options": ["Sole Proprietorship", "Partnership Firm", "Private Limited Company", "LLP"], "correct": 2},
            {"question": "What is the typical vesting cliff period for founder/employee equity?", "options": ["3 months", "6 months", "1 year", "2 years"], "correct": 2},
            {"question": "For FDI compliance, which instrument is preferred to avoid debt classification?", "options": ["NCD", "CCD (Compulsorily Convertible Debenture)", "OCD", "NCD"], "correct": 1},
            {"question": "Within how many days of receiving foreign investment must FCGPR be filed with RBI?", "options": ["15 days", "30 days", "60 days", "90 days"], "correct": 1},
            {"question": "What is the DPIIT tax exemption period for DPIIT-recognized startups?", "options": ["1 year", "2 years", "3 years", "5 years"], "correct": 2},
        ],
    },
    {
        "id": "criminal-procedure",
        "title": "Criminal Law & CrPC Basics",
        "level": "Intermediate",
        "description": "Understand FIR filing, bail, arrest procedures, trial process, and appeals in Indian criminal courts.",
        "duration_hours": 4,
        "lessons_count": 5,
        "category": "Criminal Law",
        "image_emoji": "👮",
        "lessons": [
            {"id": 1, "title": "FIR - First Information Report", "content": "An FIR (First Information Report) under Section 154 CrPC is the starting point of criminal proceedings.\n\n**Who can file**: Any person who has knowledge of a cognizable offence.\n\n**Where**: Police station having jurisdiction over the area where offence occurred.\n\n**Process**:\n1. Go to police station\n2. Give information in writing or orally\n3. SHO (Station House Officer) must record it\n4. FIR must be signed by complainant\n5. You are entitled to a FREE COPY of FIR\n\n**If police refuse**: File complaint before Magistrate under Section 156(3). Send application by registered post to SP/Commissioner.\n\n**Zero FIR**: Can be filed at any police station regardless of jurisdiction; transferred to appropriate station.\n\n**Section 154(3)**: If SHO refuses, complain to SP in writing. SP must investigate or direct registration.", "duration_mins": 20},
            {"id": 2, "title": "Cognizable vs Non-Cognizable Offences", "content": "**Cognizable Offence**: Police can arrest WITHOUT a warrant.\nExamples: Murder (302), Robbery (392), Rape (376), Kidnapping (363), Dacoity (395)\n\n**Non-Cognizable Offence**: Police CANNOT arrest without a warrant. Must get Magistrate's permission.\nExamples: Cheating (420) in some cases, Public nuisance, Assault without grievous hurt\n\n**Bailable Offence**: Bail is a right, must be granted.\nExamples: Most minor offences, Section 498A (but practically treated as non-bailable)\n\n**Non-Bailable Offence**: Bail is discretionary with court.\nExamples: Murder, Rape, Dacoity, Arms Act offences\n\n**First Schedule CrPC**: Contains classification of all IPC offences as cognizable/non-cognizable, bailable/non-bailable.", "duration_mins": 20},
            {"id": 3, "title": "Bail - Types and How to Get Bail", "content": "**Types of Bail**:\n\n**Regular Bail (S.437/439 CrPC)**:\n- S.437: Before Magistrate (in non-bailable offences)\n- S.439: Before Sessions Court\n- Discretionary\n- Factors: Nature of accusation, evidence, fear of flight, interference with witnesses\n\n**Anticipatory Bail (S.438 CrPC)**:\n- Applied BEFORE arrest\n- Before Sessions Court or High Court\n- Landmark: Gurbaksh Singh Sibbia v. State of Punjab (1980) - liberal view on anticipatory bail\n- Cannot be rejected mechanically\n\n**Default Bail (S.167(2) CrPC)**:\n- If chargesheet not filed within 60-90 days, accused entitled to bail as a matter of right\n\n**Supreme Court bail jurisprudence**: Bail is the rule, jail is the exception. Arnesh Kumar judgment changed police practice for 498A cases.", "duration_mins": 25},
            {"id": 4, "title": "Trial Procedure", "content": "**Stages of Criminal Trial**:\n\n1. **Cognizance**: Court takes cognizance of offence from Police Report (Chargesheet) or Complaint\n\n2. **Committal to Sessions**: In Sessions triable cases, Magistrate commits case to Sessions Court\n\n3. **Framing of Charges**: Accused told what charge they face. If no case: discharge.\n\n4. **Plea of Guilty**: If guilty, sentenced. If not guilty, trial proceeds.\n\n5. **Prosecution Evidence**: Prosecution examines witnesses. Defence cross-examines.\n\n6. **Section 313 Examination**: Accused asked about incriminating evidence. Cannot be compelled to answer.\n\n7. **Defence Evidence**: Optional. Accused can examine witnesses.\n\n8. **Final Arguments**: Both sides argue.\n\n9. **Judgment**: Acquittal or Conviction. If conviction, hear on sentence.\n\n**Important**: You have right to legal representation at all stages.", "duration_mins": 20},
            {"id": 5, "title": "Appeals and Revisions", "content": "**Criminal Appeals**:\n\nFrom Magistrate → Sessions Court (Section 374 CrPC)\nFrom Sessions Court → High Court (Section 374)\nFrom High Court → Supreme Court (Article 136 SLP)\n\n**Limitation for Appeal**: 30 days from sentence (in most cases)\n\n**Revision (Section 397-401)**: High Court can revise any order for correctness, legality, propriety. Important for interlocutory orders.\n\n**Transfer Petition (Section 406)**: SC can transfer case from one state to another.\n\n**Acquittal Appeal**: State can appeal against acquittal. Very strict standard: Perverse or against weight of evidence.\n\n**Bail during appeal**: Can apply for suspension of sentence under Section 389 while appeal pending.", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Under which Section of CrPC must police register an FIR?", "options": ["Section 41", "Section 154", "Section 167", "Section 174"], "correct": 1},
            {"question": "Anticipatory bail is provided under which Section of CrPC?", "options": ["Section 437", "Section 438", "Section 439", "Section 440"], "correct": 1},
            {"question": "If chargesheet is not filed within statutory period, accused is entitled to:", "options": ["Automatic acquittal", "Default bail as a matter of right", "Transfer to higher court", "Stay of proceedings"], "correct": 1},
            {"question": "Which court hears appeal from a Magistrate's conviction?", "options": ["High Court", "Sessions Court", "Chief Judicial Magistrate", "Supreme Court"], "correct": 1},
            {"question": "In cognizable offences, police can arrest:", "options": ["Only with warrant", "Without warrant", "Only with Magistrate permission", "Only after FIR"], "correct": 1},
        ],
    },
    {
        "id": "family-law",
        "title": "Family Law in India",
        "level": "Intermediate",
        "description": "Navigate divorce, maintenance, child custody, domestic violence, and inheritance under Hindu, Muslim, and secular laws.",
        "duration_hours": 3.5,
        "lessons_count": 5,
        "category": "Family Law",
        "image_emoji": "👨‍👩‍👧",
        "lessons": [
            {"id": 1, "title": "Divorce Laws in India", "content": "India has different divorce laws for different religions:\n\n**Hindu Marriage Act, 1955 (Hindus, Buddhists, Jains, Sikhs)**:\n- Mutual Consent: Section 13B - 1 year separation, 6-18 months cooling period (waivable per Amardeep Singh judgment)\n- Contested: Grounds include cruelty, desertion (2 years), adultery, conversion, mental disorder, leprosy\n\n**Muslim Personal Law**:\n- Talaq (by husband), Khula (by wife), Mubarat (mutual)\n- Triple Talaq abolished by Muslim Women (Protection of Rights on Marriage) Act, 2019\n\n**Special Marriage Act, 1954**: For inter-religion marriages, court marriage\n- 1 month notice period, any person can object\n\n**Indian Divorce Act, 1869**: For Christians\n\n**Parsi Marriage and Divorce Act, 1936**: For Parsis", "duration_mins": 25},
            {"id": 2, "title": "Maintenance and Alimony", "content": "**Types of Maintenance**:\n\n**Interim Maintenance**: Granted during pendency of case. Can be claimed immediately.\n\n**Permanent Alimony**: After divorce. Court considers: Income of both, lifestyle during marriage, assets.\n\n**Section 125 CrPC**: Non-religious maintenance for wife, children, parents. Fast remedy. Any court.\n\n**Section 24 Hindu Marriage Act**: Pendente lite (during case) maintenance if spouse has no independent income.\n\n**Factors for quantum**:\n- Income and assets of both parties\n- Standard of living during marriage\n- Contribution of wife during marriage\n- Children's needs\n\n**Rajnesh v. Neha (2021)**: SC laid down guidelines for maintenance. Mandatory disclosure of assets. One forum rule.\n\n**Important**: You can claim maintenance even without filing for divorce.", "duration_mins": 25},
            {"id": 3, "title": "Child Custody", "content": "**Legal Framework**: Guardians and Wards Act, 1890 + Hindu Minority and Guardianship Act, 1956\n\n**Test**: Best interests of the child. No automatic right of either parent.\n\n**Types of Custody**:\n- Sole Custody: One parent has custody, other gets visitation\n- Joint Custody: Both parents share custody\n- Physical vs Legal Custody\n\n**Mother's preference**: For children below 5 years, mother usually gets custody unless unfit.\n\n**Process**: File petition in Family Court. Child's voice considered for older children (usually 9+).\n\n**International**: Hague Convention on Child Abduction - India not a signatory but courts apply principles.\n\n**Modification**: Custody orders can be modified on change of circumstances.", "duration_mins": 20},
            {"id": 4, "title": "Domestic Violence Act", "content": "**Protection of Women from Domestic Violence Act, 2005** is a civil remedy.\n\n**Who can apply**: Wife, live-in partner, daughter, mother, sister - any woman in domestic relationship.\n\n**Types of Domestic Violence**:\n- Physical: Assault, beating\n- Sexual: Marital rape, forced sexual acts\n- Verbal/Emotional: Abuse, insults\n- Economic: Denial of money, assets\n\n**Reliefs available**:\n- Protection Order: Prevent respondent from committing DV\n- Residence Order: Right to live in shared household\n- Monetary Relief: Maintenance, medical expenses\n- Custody Order\n- Compensation\n\n**Process**: File application before Magistrate or Protection Officer. Interim orders within same day possible.\n\n**Shelter homes**: Victim can go to government shelter homes.", "duration_mins": 20},
            {"id": 5, "title": "Succession and Inheritance", "content": "**Hindu Succession Act, 1956** (as amended 2005):\n- Class I heirs: Son, daughter, widow, mother get equal share\n- 2005 amendment: Daughters have equal coparcenary rights in ancestral property\n\n**Muslim Law**:\n- Hanafi law: Fixed shares for heirs. Daughter gets half of son's share.\n- Bequest: Maximum 1/3rd of estate can be willed away\n\n**Indian Succession Act, 1925**:\n- For Christians and Parsis\n- Spouse + children share 1/3 + 2/3\n\n**Will (Vasiyat)**:\n- Any person of sound mind above 18 can make a will\n- Must be signed by testator and 2 witnesses\n- Registration recommended but not mandatory\n- Probate required in some cases\n\n**Nomination is NOT inheritance**: Bank nomination doesn't override succession law.", "duration_mins": 20},
        ],
        "quiz": [
            {"question": "Under which Section of Hindu Marriage Act is mutual consent divorce filed?", "options": ["Section 9", "Section 13", "Section 13B", "Section 25"], "correct": 2},
            {"question": "Section 125 CrPC provides maintenance for:", "options": ["Wife only", "Wife and children only", "Wife, children, and parents", "All family members"], "correct": 2},
            {"question": "The 2005 amendment to Hindu Succession Act gave daughters:", "options": ["Right to will", "Equal coparcenary rights in ancestral property", "Double inheritance share", "Right to be Karta"], "correct": 1},
            {"question": "The Protection of Women from Domestic Violence Act, 2005 provides:", "options": ["Criminal punishment only", "Civil remedies including protection orders", "Both civil and criminal remedies equally", "Only monetary compensation"], "correct": 1},
            {"question": "For a child below 5 years, who generally gets custody?", "options": ["Father automatically", "Mother generally preferred unless unfit", "Court-appointed guardian", "Grandparents"], "correct": 1},
        ],
    },
    {
        "id": "property-law",
        "title": "Property Law in India",
        "level": "Intermediate",
        "description": "Master property transactions, documentation, tenant-landlord relations, and dispute resolution in Indian real estate.",
        "duration_hours": 3,
        "lessons_count": 4,
        "category": "Property Law",
        "image_emoji": "🏠",
        "lessons": [
            {"id": 1, "title": "Property Documents", "content": "**Essential Documents for any property**:\n\n1. **Title Deed/Sale Deed**: Primary ownership document. Must be registered.\n2. **Encumbrance Certificate (EC)**: Shows all transactions on property for a period. Issued by sub-registrar.\n3. **Khata/Property Card**: Municipal record of property ownership and tax payment.\n4. **Revenue Records (7/12 extract for agricultural land)**: Government land record.\n5. **Building Plan Approval**: Approved plan from local authority (BBMP, BMC, etc.)\n6. **Occupancy Certificate (OC)**: Certificate that building is fit for occupation.\n7. **Completion Certificate**: Building completed as per approved plan.\n\n**Before buying**: Get minimum 15-30 years EC. Check for mortgages, litigations, attachments.\n\n**Stamp Duty**: 5-7% of market value (varies by state). Must pay before/at registration.\n**Registration Fee**: 1% of market value.", "duration_mins": 20},
            {"id": 2, "title": "Sale Transaction Process", "content": "**Process for buying property in India**:\n\n1. **Due Diligence**: Verify title through EC, check for disputes, loans\n2. **Agreement to Sell**: Preliminary agreement. Pay token amount (5-10%). Not registered usually.\n3. **Sale Deed Draft**: Prepare sale deed with all details.\n4. **Pay Stamp Duty**: Pay online/at bank before registration.\n5. **Registration**: Both parties appear at Sub-Registrar's office with documents and witnesses.\n6. **Mutation/Khata Transfer**: Update municipal records in buyer's name.\n\n**Power of Attorney Sales**: SC banned PoA sales for immovable property (Suraj Lamp Industries, 2012). Only registered Sale Deed is valid.\n\n**NRI property**: NRIs can buy residential and commercial property in India. FEMA compliance required.\n\n**Agricultural land**: NRIs and foreigners generally cannot buy agricultural land.", "duration_mins": 25},
            {"id": 3, "title": "Tenant-Landlord Rights", "content": "**Tenant Rights**:\n- Landlord cannot evict without court order\n- No forcible entry into premises\n- Peaceful enjoyment of property\n- Deposit refund on vacation (after deductions)\n- Receipt for rent paid\n\n**Landlord Rights**:\n- Receive rent on time\n- Inspect property with reasonable notice\n- Evict tenant for non-payment, misuse, personal need (under Rent Control Acts)\n\n**Eviction Process**:\n1. Send termination notice (typically 30-90 days)\n2. File eviction petition in Rent Controller Court (if Rent Control Act applies) or Civil Court\n3. Obtain eviction decree\n4. Execute decree\n\n**Rent Control Act**: State law. Applies to premises below certain rent limits. Gives tenants strong protection against eviction and rent increase.\n\n**Caution**: Once tenant occupies for years, eviction becomes difficult.", "duration_mins": 20},
            {"id": 4, "title": "RERA for Homebuyers", "content": "**RERA (Real Estate Regulation and Development Act, 2016)** protects flat buyers.\n\n**Before RERA problems**: Builders took money, delayed projects, changed plans, diverted funds.\n\n**RERA Solutions**:\n- Mandatory registration of projects with > 8 units or > 500 sq m\n- 70% of buyer money must go to separate escrow account\n- Changes to plan only with 2/3 buyer consent\n- Structural defects liability for 5 years\n\n**Your RERA Rights**:\n1. Access project information on RERA website\n2. Refund with interest if builder delays\n3. Claim compensation for false representations\n4. File complaint before State RERA Authority\n\n**Complaint Process**: File on State RERA portal. Adjudicating Officer determines within 60 days.\n\n**Check RERA registration**: Every state has RERA portal (maharera.mahaonline.gov.in, rera.karnataka.gov.in, etc.)", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Which document shows all transactions on a property for a specific period?", "options": ["Khata Certificate", "Encumbrance Certificate", "Sale Deed", "Title Certificate"], "correct": 1},
            {"question": "The Supreme Court banned property sales through:", "options": ["Sale Deed", "Power of Attorney", "Agreement to Sell", "Gift Deed"], "correct": 1},
            {"question": "Under RERA, what percentage of buyer money must go to escrow?", "options": ["50%", "60%", "70%", "80%"], "correct": 2},
            {"question": "RERA is applicable to projects with more than how many units?", "options": ["4 units", "8 units", "10 units", "20 units"], "correct": 1},
            {"question": "For structural defects in a RERA project, builder is liable for how many years?", "options": ["2 years", "3 years", "5 years", "10 years"], "correct": 2},
        ],
    },
    {
        "id": "labour-law",
        "title": "Labour Law for Employees",
        "level": "Beginner",
        "description": "Know your rights as an employee in India - minimum wages, PF, gratuity, maternity leave, termination, and workplace safety.",
        "duration_hours": 2,
        "lessons_count": 4,
        "category": "Labour Law",
        "image_emoji": "👷",
        "lessons": [
            {"id": 1, "title": "Employee Rights Overview", "content": "**Minimum Wages Act, 1948**:\n- State-wise minimum wages for different categories\n- Unskilled, semi-skilled, skilled workers\n- Enhanced for special localities\n\n**Factories Act, 1948**:\n- Max 48 hours/week, 9 hours/day\n- Overtime: Double wages\n- 1 day rest per week\n- Crèche for 30+ women workers\n\n**Shops and Establishments Act**: State-specific. Covers shops, offices, commercial establishments.\n\n**Payment of Wages Act, 1936**:\n- Wages on time (by 7th of following month for <1000 employees)\n- Deductions only as prescribed\n\n**Code on Wages, 2019**: Consolidates 4 wage laws. Not yet fully implemented.", "duration_mins": 20},
            {"id": 2, "title": "Provident Fund and Gratuity", "content": "**Provident Fund (EPF)**:\n- Mandatory for establishments with 20+ employees\n- Employee: 12% of basic salary\n- Employer: 12% (8.33% to EPS pension, 3.67% to EPF)\n- Current rate: 8.25% per annum\n- Withdrawal: On retirement (58 years), 2+ months unemployment, certain purposes\n\n**Gratuity (Payment of Gratuity Act, 1972)**:\n- Payable on: Retirement, resignation after 5 years, death, disablement\n- Formula: 15 days' wages × years of service ÷ 26\n- Maximum: ₹20 lakh\n- Payable within 30 days\n\n**ESI (ESIC)**:\n- Employees earning up to ₹21,000/month\n- 0.75% employee, 3.25% employer\n- Covers medical, maternity, disability, death benefits", "duration_mins": 20},
            {"id": 3, "title": "Termination and Retrenchment", "content": "**Industrial Disputes Act, 1947**:\n\n**Section 25F**: Retrenchment compensation = 15 days' wages for each completed year of service\n\n**Chapter VB**: Establishments with 100+ workers need government permission before retrenchment/closure.\n\n**Notice Period**: Depends on employment contract. Minimum as per Shops and Establishments Act.\n\n**Wrongful Termination**: Can approach Labour Court under Industrial Disputes Act. Must exhaust domestic remedies.\n\n**Non-compliance**: Employer cannot terminate without following proper procedure for 'workmen' (not managerial staff).\n\n**Who is a workman**: Not supervisory/managerial/administrative staff earning above ₹15,000/month (varies by state). Key for coverage under ID Act.", "duration_mins": 20},
            {"id": 4, "title": "Maternity and POSH", "content": "**Maternity Benefit Act, 1961 (amended 2017)**:\n- 26 weeks paid maternity leave (for up to 2 children)\n- 12 weeks for 3rd+ child\n- 12 weeks for adoption\n- Crèche facility mandatory for 50+ employees\n- Work from home option after leave\n\n**POSH Act, 2013**:\n- Mandatory ICC (Internal Complaints Committee) for 10+ employees\n- ICC: Presiding officer (senior woman) + 2 internal members + 1 external NGO member\n- Complaint within 3 months\n- Enquiry: 90 days\n- Action: Termination, fine, counselling\n\n**Rights**: Confidentiality, no retaliation for complainant. Conciliation before inquiry possible.\n\n**Non-compliance penalty**: ₹50,000 fine, cancellation of licence.", "duration_mins": 20},
        ],
        "quiz": [
            {"question": "What is the formula for gratuity calculation?", "options": ["15 days wages × years / 30", "15 days wages × years / 26", "1 month wages × years", "30 days wages × years / 26"], "correct": 1},
            {"question": "Establishments with how many workers need government permission for retrenchment?", "options": ["50+", "100+", "200+", "300+"], "correct": 1},
            {"question": "Maternity leave under the amended 2017 Act is how many weeks for first two children?", "options": ["12 weeks", "16 weeks", "26 weeks", "52 weeks"], "correct": 2},
            {"question": "Under POSH Act, complaint must be filed within how many months of incident?", "options": ["1 month", "2 months", "3 months", "6 months"], "correct": 2},
            {"question": "ESI applies to employees earning up to how much per month?", "options": ["₹15,000", "₹18,000", "₹21,000", "₹25,000"], "correct": 2},
        ],
    },
    {
        "id": "cyber-law",
        "title": "Cyber Law & Digital Rights",
        "level": "Intermediate",
        "description": "Understand the IT Act, data privacy, cyber crimes, online fraud, and your digital rights in India.",
        "duration_hours": 2.5,
        "lessons_count": 4,
        "category": "Cyber Law",
        "image_emoji": "💻",
        "lessons": [
            {"id": 1, "title": "IT Act 2000 and Cyber Crimes", "content": "**Information Technology Act, 2000** is India's primary cyber law.\n\n**Key offences and punishment**:\n- Section 66: Computer-related offences (hacking) - 3 years + fine\n- Section 66A: Struck down by Supreme Court (Shreya Singhal, 2015) for free speech violation\n- Section 66B: Dishonestly receiving stolen computer resource - 3 years + ₹1 lakh fine\n- Section 66C: Identity theft - 3 years + ₹1 lakh fine\n- Section 66D: Cheating by personation - 3 years + ₹1 lakh fine\n- Section 66E: Violation of privacy (recording intimate images) - 3 years + ₹2 lakh\n- Section 67: Publishing obscene material - 3-5 years + fine\n- Section 67B: Child pornography - 5-7 years + fine\n- Section 72: Breach of confidentiality by intermediary - 2 years\n\n**Cybercrime portal**: cybercrime.gov.in for reporting", "duration_mins": 25},
            {"id": 2, "title": "Data Privacy in India", "content": "**Personal Data Protection**: India passed the Digital Personal Data Protection Act, 2023.\n\n**Key provisions**:\n- Data principals have rights: access, correction, erasure, grievance redressal\n- Data fiduciaries (companies) must:\n  - Get valid consent\n  - Use data only for specified purpose\n  - Implement security safeguards\n  - Report data breaches to DPDB board\n- Data Protection Board of India (DPDB): Adjudicatory body\n- Significant Data Fiduciaries: Higher obligations (DPDPA)\n\n**Penalties**: Up to ₹250 crore for significant breaches\n\n**Previous**: Section 43A IT Act - compensation for negligent handling of sensitive personal data\n\n**Workplace privacy**: Employers can monitor work computers but must inform employees.", "duration_mins": 20},
            {"id": 3, "title": "Online Fraud and Remedies", "content": "**Common cyber frauds in India**:\n- UPI fraud: Requests for OTP, fake UPI handles\n- KYC fraud: Fake bank/KYC calls\n- Job scams: Fake job offers with upfront payment\n- Investment fraud: Fake trading platforms\n- Romance scam: Fake relationships leading to money requests\n\n**What to do if defrauded**:\n1. Immediately call bank (in case of UPI/card fraud)\n2. Report at cybercrime.gov.in or helpline 1930\n3. File FIR at police station (Cyber Crime Cell)\n4. Report to RBI (banking fraud)\n5. File complaint with SEBI (investment fraud)\n\n**Chargeback**: For credit card fraud, file chargeback within 90 days.\n\n**RBI circular**: Zero liability for innocent victims of online banking fraud if reported within 3 days.", "duration_mins": 20},
            {"id": 4, "title": "Social Media Rights", "content": "**Your rights on social media**:\n- Right to be forgotten: Can request deletion of your data\n- Grievance redressal: Social media platforms must have grievance officer in India\n- 15 days: Time for platforms to respond to complaints\n- Significant Social Media Intermediary: 50 lakh+ users; must appoint Chief Compliance Officer, Nodal Officer, Grievance Officer in India\n\n**IT Rules, 2021**: New regulations for intermediaries and social media\n\n**Fake news**: No government censorship authority; platforms must remove illegal content within 24-72 hours of government order\n\n**Defamation online**: Can file criminal complaint under IPC Section 499-500 or IT Act. Intermediaries protected if they act as passive hosts (Section 79 safe harbour).\n\n**Cyberbullying**: Report to platform + cybercrime portal. Section 66A gone, use IPC sections 294 (obscene acts), 507 (criminal intimidation by anonymous communication).", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Which Section of IT Act deals with identity theft?", "options": ["Section 66B", "Section 66C", "Section 66D", "Section 66E"], "correct": 1},
            {"question": "The cybercrime helpline number in India is:", "options": ["100", "112", "1930", "1800-11-4000"], "correct": 2},
            {"question": "The Digital Personal Data Protection Act, 2023 penalty can go up to:", "options": ["₹1 crore", "₹50 crore", "₹250 crore", "₹500 crore"], "correct": 2},
            {"question": "Under RBI circular, zero liability for online banking fraud applies if reported within:", "options": ["24 hours", "3 days", "7 days", "30 days"], "correct": 1},
            {"question": "Which Section provides safe harbour to internet intermediaries?", "options": ["Section 43A", "Section 66", "Section 72", "Section 79"], "correct": 3},
        ],
    },
    {
        "id": "rti-mastery",
        "title": "RTI Mastery - Transparency Tool",
        "level": "Beginner",
        "description": "Use the Right to Information Act to get government information, fight corruption, and hold officials accountable.",
        "duration_hours": 1.5,
        "lessons_count": 3,
        "category": "RTI",
        "image_emoji": "📋",
        "lessons": [
            {"id": 1, "title": "RTI Basics and Scope", "content": "**Right to Information Act, 2005** is one of India's most powerful transparency laws.\n\n**Who can file**: Any citizen of India (not companies, NRIs or foreign nationals)\n\n**Who must provide**: All public authorities under Central/State governments. Includes:\n- Central and State ministries\n- Municipal corporations\n- PSUs (BSNL, ONGC, etc.)\n- Universities (central/state)\n- NGOs receiving substantial government funding\n\n**What you can ask**:\n- Government documents and files\n- Decisions and reasons for decisions\n- Status of applications\n- Information about employees\n- Budget and expenditure details\n- Information about schemes\n\n**What is exempt (Section 8)**:\n- Security/intelligence information\n- Cabinet notes until decision\n- Personal information not serving public interest\n- Commercially confidential\n- Court-sealed documents", "duration_mins": 20},
            {"id": 2, "title": "Filing RTI Application", "content": "**How to file RTI**:\n\n**Online**: rtionline.gov.in (Central Government)\n**Offline**: Write to PIO of the department\n\n**Application must contain**:\n- Your name and address\n- Specific information you want\n- Time period if relevant\n- How you want information (inspect, copy, etc.)\n- Application fee payment details\n\n**Fee**: ₹10 (central) for application. Subsequent pages at ₹2 each. Free for BPL.\n\n**Timeline**:\n- 30 days: Normal response time\n- 48 hours: If information concerns life or liberty\n- 40 days: If transferred to another department\n\n**If no response in 30 days**: Can file First Appeal. Deemed refusal.\n\n**Tips for good RTI**:\n- Be specific, not vague\n- Ask one subject per RTI (easier for PIO)\n- Don't ask why or reasons (that's explanation, not information)\n- Ask for certified copies of documents", "duration_mins": 25},
            {"id": 3, "title": "First and Second Appeals", "content": "**First Appeal**:\n- File within 30 days of response/non-response\n- Before First Appellate Authority (FAA) of same department (senior to PIO)\n- Decision within 30 days (45 days with reasons)\n- Free, no additional fee\n\n**Second Appeal**:\n- File within 90 days of FAA's response/non-response\n- Before Central Information Commission (CIC) or State Information Commission (SIC)\n- Online: cic.gov.in, or by post\n- CIC can impose penalty: ₹250/day up to ₹25,000 on PIO for non-compliance\n- Can also recommend disciplinary action\n\n**Compensation**: If PIO has caused detriment to applicant, CIC can award compensation.\n\n**Common Strategies**:\n- File RTI before filing complaint - know the facts\n- Use RTI to track status of pending cases/applications\n- RTI can reveal discrimination and corruption\n- Parliamentary committees use RTI findings\n\n**Watan Banao**: Many activist groups help file RTIs for common people", "duration_mins": 15},
        ],
        "quiz": [
            {"question": "Who can file an RTI in India?", "options": ["Any person", "Indian citizens only", "Indian citizens and NRIs", "All except minors"], "correct": 1},
            {"question": "What is the standard response time for an RTI application?", "options": ["15 days", "30 days", "45 days", "60 days"], "correct": 1},
            {"question": "If the information concerns life or liberty, response time is:", "options": ["24 hours", "48 hours", "7 days", "15 days"], "correct": 1},
            {"question": "Maximum penalty CIC can impose on PIO for non-compliance is:", "options": ["₹5,000", "₹10,000", "₹25,000", "₹50,000"], "correct": 2},
            {"question": "Second appeal against RTI rejection goes to:", "options": ["High Court", "Supreme Court", "Information Commission (CIC/SIC)", "Ombudsman"], "correct": 2},
        ],
    },
]


class QuizSubmission(BaseModel):
    answers: list[int]


@router.get("/courses")
async def list_courses():
    return [
        {k: v for k, v in c.items() if k not in ("lessons", "quiz")}
        for c in COURSES
    ]


@router.get("/courses/{course_id}")
async def get_course(course_id: str):
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/courses/{course_id}/quiz/submit")
async def submit_quiz(course_id: str, submission: QuizSubmission):
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course or "quiz" not in course:
        raise HTTPException(status_code=404, detail="Course or quiz not found")

    quiz = course["quiz"]
    answers = submission.answers

    correct = sum(1 for i, q in enumerate(quiz) if i < len(answers) and answers[i] == q["correct"])
    total = len(quiz)
    score = round((correct / total) * 100)

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "passed": score >= 60,
        "message": "Congratulations! You passed!" if score >= 60 else "Keep studying and try again!",
        "results": [
            {
                "question": q["question"],
                "your_answer": answers[i] if i < len(answers) else None,
                "correct_answer": q["correct"],
                "is_correct": i < len(answers) and answers[i] == q["correct"],
            }
            for i, q in enumerate(quiz)
        ],
    }
