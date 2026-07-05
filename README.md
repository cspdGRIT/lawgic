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
