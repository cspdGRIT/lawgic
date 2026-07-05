Complete Pricing Breakdown — Lawgic Production Stack
Infrastructure (Monthly)
Service	What For	Free Tier	Paid
Vercel	Frontend hosting	✅ Free forever	$20/mo Pro (not needed early)
Railway	Backend + PostgreSQL	$5 credit/mo trial	~$10-15/mo total
Cloudflare R2	Document storage	✅ 10GB free	$0.015/GB after
Cloudflare	CDN + DDoS	✅ Free plan	—
Infrastructure total: ~₹1,200/mo to start

AI / LLM
Option	Quality	Cost
Anthropic Claude claude-sonnet-4-6 (current)	Best	~$3 per 1M tokens ≈ ₹250/mo at low volume
Groq (Llama 3.3 70B)	Very good	✅ Free tier (30 req/min) → $0.59/M tokens paid
OpenAI GPT-4o mini	Good	$0.15/M input tokens
Ollama self-hosted	Decent	✅ Free (need GPU server ~$20/mo on Vast.ai)
Recommendation: Start with Groq free tier → move to Claude when revenue comes in

Legal Data
Service	What For	Cost
Indian Kanoon API	Real case law, judgments	✅ Free (non-commercial) → ₹5,000/mo commercial
VakilSearch API	Company/MCA data	₹2,000-5,000/mo
eCourts API	Case status lookup	✅ Free (government)
India Code (legislation.gov.in)	Bare acts, statutes	✅ Free
Legal data total: ₹0 to start (use free tiers), ₹5,000-7,000/mo at scale

Payments
Service	Setup Cost	Per Transaction
Razorpay	✅ Free	2% + ₹3 per transaction
Cashfree	✅ Free	1.75% per transaction
PayU	✅ Free	2% per transaction
Recommendation: Razorpay — best docs, easiest integration in India

Communication
Service	What For	Free Tier	Paid
Resend	Transactional email (OTP, receipts)	3,000 emails/mo	$20/mo for 50k
Twilio / MSG91	SMS OTP	—	₹0.20 per SMS
MSG91	WhatsApp notifications	—	₹0.35 per message
Firebase	Push notifications	✅ Free	—
Comms total: ₹0 early, ~₹500-2,000/mo at scale

Video Consultations
Option	Cost	Notes
Jitsi Meet (self-hosted)	✅ Free	Host on your Railway server
Daily.co	10,000 min/mo free	$0.004/min after
Agora.io	10,000 min/mo free	Best quality, good SDK
100ms	10,000 min/mo free	Indian startup, good support
Recommendation: 100ms — Indian company, free tier generous, good docs

Auth & Security
Service	What For	Cost
Current JWT system	Already built	✅ Free
Google OAuth	Social login	✅ Free
Let's Encrypt via Cloudflare	SSL/HTTPS	✅ Free
Domain & Brand
Item	Cost
.in domain (e.g. lawgic.in)	₹800-1,200/year
.com domain	$12/year (~₹1,000)
Logo (if needed)	₹0 — already have it
Total Cost Summary
Stage	Monthly Cost	What You Get
MVP launch	₹1,500-2,000/mo	Vercel + Railway + Groq free + Razorpay
Growth (100 users)	₹5,000-8,000/mo	+ Indian Kanoon commercial + SMS + video
Scale (1000+ users)	₹15,000-25,000/mo	+ Claude API + dedicated DB + CDN
Break-even Math
At the ₹999/mo Pro plan:

2 paying subscribers covers your MVP hosting cost
8 paying subscribers covers everything including Indian Kanoon API
Want me to start wiring Razorpay and PostgreSQL migration first — those two unlock real revenue and make it deploy-ready?