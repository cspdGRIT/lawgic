# Lawgic — AI-Powered Legal Intelligence for India

> Democratizing legal access for India's 1.4 billion people through advanced AI

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35)](https://langchain-ai.github.io/langgraph)
[![Claude](https://img.shields.io/badge/Claude-Sonnet_4.6-D4A017)](https://anthropic.com)

## What is Lawgic?

Lawgic is a full-stack AI-powered legal tech platform purpose-built for India. It combines a **multi-agent AI system** (6 specialized agents) with a professional React frontend to deliver:

- **Case Outcome Prediction** — AI analysis with confidence scores and legal reasoning
- **AI Legal Document Generator** — 30+ Indian legal document templates
- **Lawyer Marketplace** — AI-powered matching with verified lawyers
- **Legal Research** — Search IPC, CrPC, Consumer Act, RERA, and 100+ cases
- **Multilingual Support** — 22 Indian languages
- **Legal Education Hub** — 10 courses with quizzes and progress tracking

---

## Architecture

```
lawgic/
├── backend/          # FastAPI + LangGraph multi-agent system
│   ├── app/
│   │   ├── agents/   # 6 specialized LangGraph agents
│   │   ├── api/      # REST API + WebSocket routes
│   │   ├── core/     # Config, DB, Security
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic v2 schemas
│   │   └── services/ # Claude AI service
│   └── seed_data.py  # 30 lawyer profiles seeded
└── frontend/         # React 18 + TypeScript + Tailwind
    └── src/
        ├── pages/    # Landing, Dashboard, Chat, Case Analysis, Documents...
        ├── components/
        └── store/    # Zustand state management
```

### Multi-Agent System (LangGraph)

```
User Query
    │
    ▼
Intent Classifier
    ├──► Case Analysis Agent    → Win probability, strategy, next steps
    ├──► Document Drafting Agent → 30+ legal templates, complete drafts
    ├──► Legal Research Agent   → Indian statutes, landmark cases
    ├──► Translation Agent      → 22 Indian languages
    └──► Lawyer Matching Agent  → Ranked recommendations
                    │
                    ▼
           Synthesizer → Streaming Response (WebSocket / SSE)
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Anthropic API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY and SECRET_KEY

# Seed database with 30 lawyer profiles
python seed_data.py

# Start server (auto-reload)
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173

### Docker (Full Stack)

```bash
cp backend/.env.example .env
# Fill in ANTHROPIC_API_KEY and SECRET_KEY
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register as client or lawyer |
| POST | `/api/v1/auth/login` | Login, receive JWT |
| GET | `/api/v1/cases` | List user's cases |
| POST | `/api/v1/cases` | Create new case |
| POST | `/api/v1/cases/{id}/analyze` | **SSE** — AI case analysis stream |
| GET | `/api/v1/documents/templates` | 30+ document templates |
| POST | `/api/v1/documents/generate` | **SSE** — AI document generation stream |
| GET | `/api/v1/lawyers` | Search lawyers (city, area, rating, fee) |
| POST | `/api/v1/lawyers/match` | AI lawyer matching |
| POST | `/api/v1/research/search` | Search Indian legal database |
| WS | `/api/v1/chat/ws/{session}` | **WebSocket** — streaming AI chat |
| GET | `/api/v1/education/courses` | 10 legal education courses |

---

## Legal Templates (30+)

| Category | Templates |
|----------|-----------|
| **Notices** | Legal Notice, Cheque Bounce (Sec 138 NI Act), Demand Notice |
| **Agreements** | Rental, Leave & License, Sale Deed, Employment, NDA, MOU |
| **Corporate** | Partnership Deed, Power of Attorney (General/Specific) |
| **Court Filings** | Bail Application, Anticipatory Bail, Writ Petitions (Habeas Corpus/Mandamus/Certiorari), PIL |
| **Family Law** | Divorce (Mutual/Contested), Child Custody, Affidavit, Will & Testament |
| **Consumer/RTI** | Consumer Complaint (NCDRC), RTI Application, RERA Complaint |
| **Labour** | Vakalatnama, Labour Court Complaint, FIR Complaint Letter |

---

## Indian Legal Coverage

- **Criminal**: IPC, CrPC, POCSO, NDPS Act
- **Civil**: CPC, Transfer of Property Act, Specific Relief Act
- **Corporate**: Companies Act, IBC, GST, FEMA
- **Consumer**: Consumer Protection Act 2019, RERA
- **Family**: Hindu Marriage Act, Muslim Personal Law, Special Marriage Act
- **Labour**: Industrial Disputes Act, Payment of Wages Act
- **Constitutional**: Fundamental Rights, Writs, PIL

---

## Pricing

| Plan | Price | Highlights |
|------|-------|-----------|
| **Free** | ₹0/month | 5 case analyses, 3 documents, basic research |
| **Pro** | ₹999/month | Unlimited analyses, 50 documents, all templates, priority support |
| **Enterprise** | ₹4,999/month | Dedicated legal expert, API access, white-label |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, LangGraph, SQLAlchemy, aiosqlite |
| AI | Anthropic Claude (claude-sonnet-4-6), Multi-agent orchestration |
| Auth | JWT (python-jose), bcrypt |
| Streaming | Server-Sent Events (SSE), WebSocket |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| State | Zustand, TanStack Query |
| Routing | React Router v6 |

---

## License

MIT © Lawgic Technologies Pvt. Ltd.



What's Missing Before Commercial Launch
🔴 Critical (Blocker — can't launch without)
#	What	Why it's a blocker
1	Email verification	Users can register with fake/others' emails. Zero trust.
2	Password reset flow	No "Forgot Password" → users locked out permanently
3	Razorpay → Production keys	App is in test mode. Real payments won't work.
4	GST registration + invoice generation	India mandates GST invoices for B2C/B2B SaaS
5	Razorpay webhook handler	Payment confirmation is currently synchronous only — if user closes tab mid-payment, subscription never activates
6	Privacy Policy + Terms of Service pages	Legal requirement in India. Also needed by Razorpay for live key activation
7	Custom domain + HTTPS	yourapp.render.com doesn't pass trust threshold for paying users
8	CORS locked to your domain	Currently * — any site can call your API
🟡 Important (Should have at launch)
#	What	Why
9	Transactional email (payment receipts, welcome, OTP)	No email service wired. Razorpay also requires confirmation emails
10	Admin panel	No way to manage users, refunds, or subscriptions without hitting the DB directly
11	PDF export for generated documents	Currently downloads as .txt. Lawyers expect .pdf or .docx
12	Account deletion endpoint	Required by PDPB (India's data protection law) and GDPR if you have EU users
13	Rate limiting on public routes	Login/register endpoint has no brute-force protection
14	Database backups	One accidental DROP TABLE and everything is gone
15	Error monitoring (Sentry)	You won't know about crashes in production
16	CI/CD pipeline	Manual deployments = deployment fear = slow iteration
17	Lawyer KYC/verification flow	Any user can claim to be a verified advocate today
🟢 Nice to Have (Post-launch v2)
WhatsApp notifications (critical for Indian market — more important than email)
OTP/phone login (Indians prefer mobile login over email/password)
Indian Kanoon live API integration (currently using local KB)
Hindi/regional language UI (not just AI output translation)
Aadhaar eSign integration for legally binding documents
Subscription pause (not just cancel)
Referral system
Cost Breakdown by Service
Infrastructure
Service	What it does	Free Tier	Monthly (paid)	Annual
Vercel	Frontend hosting (React/Vite)	✅ Free forever (100GB bandwidth)	$20/mo Pro (team features)	$240
Render	Backend API (FastAPI)	⚠️ Free but sleeps after 15 min	$7/mo Starter (no sleep)	$84
Neon	PostgreSQL (serverless)	✅ Free (512MB, 100 CU-hrs)	$19/mo Launch	$228
Upstash Redis	LLM cache	✅ Free (500K cmds/month)	~$10/mo (pay-as-you-go)	~$120
Domain (.in or .com)	lawgic.in	❌ None	~₹900/yr	~₹900
SSL	HTTPS	✅ Free via Let's Encrypt (all hosts above)	—	—
AI / LLM
Service	What it does	Free Tier	Cost estimate	Notes
Anthropic Claude Sonnet 4.6	Primary LLM	None (pay-per-use)	See table below	Intro pricing ends Aug 31, 2026
NVIDIA NIM	Fallback LLM	✅ 1,000 calls/day free	$0 if under limit	Good for non-critical queries
Groq	Alternative fast LLM	✅ Rate-limited free tier	$0 for low volume	Llama 3.3 70B, very fast
Claude Sonnet 4.6 cost by user count (with 60% cache hit rate from your LiteLLM cache):

Active Users	Queries/user/month	Monthly LLM cost	Annual
100	30	~$15-30	~$180-360
500	30	~$75-150	~$900-1,800
1,000	30	~$150-300	~$1,800-3,600
5,000	30	~$750-1,500	~$9,000-18,000
Costs drop significantly after August 2026 standard pricing kicks in — counterintuitively, you want to maximize caching. Your cache is already wired; just make sure REDIS_URL is set in production.

Payments
Service	Fee	Notes
Razorpay	2% + 18% GST per transaction	No setup fee, no monthly fee
On ₹999 Pro subscription	₹19.98 fee → you net ₹979	Effective ~2.36% with GST
On ₹4,999 Firm subscription	₹99.98 fee → you net ₹4,899	
Email
Service	Free Tier	Paid
Resend	✅ 3,000 emails/month free, 100/day	$20/mo for 50K
AWS SES	❌ $0.10/1,000 emails	Cheapest at scale
SendGrid	❌ Free tier removed May 2025	$19.95/mo for 50K
Recommendation: Start with Resend free — 3,000 emails/month covers you until ~500+ users.

Monitoring & DevOps
Service	Free Tier	Paid
Sentry	✅ 5K errors/month free	$26/mo
GitHub Actions	✅ 2,000 min/month free	$4/mo for more
UptimeRobot	✅ 50 monitors, 5-min checks free	$7/mo
Total Monthly Cost (Realistic Starter Stack)
Phase	What you're running	Est. monthly cost
Free (launch/test)	Vercel + Render (sleeps) + Neon + Upstash + Resend — all free tiers	~$0 (+ Claude API)
Production-ready	Vercel free + Render $7 + Neon $19 + Upstash $10 + Resend free + Sentry free + domain ₹75/mo	~$36/mo + Claude
At 500 users	Above + Claude ~$150 + Resend Pro $20	$206/mo (₹17,000/mo)
At 2,000 users	Above + bigger Render + Claude ~$500	$600/mo (₹50,000/mo)
Your Free plan users (10 queries/month) cost you almost nothing thanks to caching. Pro users at ₹999/mo pay for themselves 5x over at 500 users.

Free Deployment Right Now
Yes — you can deploy 100% free with this stack:


Frontend  →  Vercel (free, global CDN)
Backend   →  Render (free, sleeps after 15 min)
Database  →  Neon (free PostgreSQL, persists forever)
Cache     →  Upstash Redis (free, 500K cmds/month)
Email     →  Resend (free, 3000/month)
The only unavoidable cost is Anthropic API — there's no free tier. Budget ~₹2,000-5,000/month for early testing.

To actually deploy it, here are the exact steps:

Step 1 — Frontend (Vercel):


cd frontend
npm install -g vercel
vercel --prod
# Follow prompts → connects your GitHub repo
Step 2 — Database (Neon):

Go to neon.com → create project lawgic
Copy the postgresql://... connection string
Run migration: DATABASE_URL=<neon_url> .venv/bin/alembic upgrade head
Step 3 — Redis (Upstash):

Go to console.upstash.com → create Redis DB
Copy UPSTASH_REDIS_URL (it's a rediss:// URL)
Step 4 — Backend (Render):

Go to render.com → New Web Service → connect GitHub
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Set env vars: DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, SECRET_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, ENVIRONMENT=production
Step 5 — Wire them together:

Set VITE_API_URL=https://your-backend.onrender.com in Vercel environment settings
Redeploy frontend
I can't click through web UIs for you, but I can run the Vercel deploy command directly if you want — it just needs you to be logged in (vercel login) first. Say the word.

Sources:

Render Pricing
Neon PostgreSQL Pricing
Upstash Redis Pricing
Anthropic Claude API Pricing
Razorpay Payment Gateway Pricing
Resend Email Pricing
Vercel Pricing
Fly.io Pricing 2026





###############


Step 1: Neon (PostgreSQL — free forever)
Go to neon.tech → Sign up → Create project → name it lawgic
Copy the Connection string from the dashboard. It looks like:

postgresql://lawgic_owner:xxx@ep-xxx.us-east-2.aws.neon.tech/lawgic?sslmode=require
Change postgresql:// to postgresql+asyncpg:// and sslmode=require to ssl=require:

postgresql+asyncpg://lawgic_owner:xxx@ep-xxx.us-east-2.aws.

npx neonctl@latest init

postgresql://neondb_owner:npg_8IvYCu0qRDQL@ep-muddy-butterfly-atzm3a0o.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require

-->

npx neonctl@latest init

postgresql+asyncpg://neondb_owner:npg_8IvYCu0qRDQL@ep-muddy-butterfly-atzm3a0o.c-9.us-east-1.aws.neon.tech/neondb?ssl=require


https://lawgic-qy66.onrender.com


Vercel:

Step 3: Vercel (Frontend — free forever)
Go to vercel.com → Sign up → Add New Project

Import your GitHub lawgic repo

Set:

Root directory: frontend
Framework Preset: Vite (auto-detected)
Build command: npm run build
Output directory: dist
Under Environment Variables, add:

Key	Value
VITE_API_URL	https://lawgic-api.onrender.com (your Render URL from Step 2)
Click Deploy. Copy the Vercel URL: https://lawgic.vercel.app



https://lawgic-bdh2sud8d-lawgicai1.vercel.app