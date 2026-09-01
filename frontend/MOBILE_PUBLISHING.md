# Publishing Lawgic to the App Store and Play Store

This tracks exactly what's done, what's blocked on this machine, and what only you
can do (accounts, payment, final submit). Capacitor wraps the existing web app
unchanged — see `capacitor.config.ts` and the `android/` / `ios/` folders.

## Status

| Step | Android | iOS |
|---|---|---|
| Capacitor project scaffolded | ✅ | ✅ |
| App icon + splash screen (branded) | ✅ | ✅ |
| Native build toolchain | ✅ (SDK, emulator, JDK 21 all installed) | ❌ needs Xcode |
| Debug build verified on-device | ✅ (emulator, real login flow) | ❌ blocked on Xcode |
| Release signing | ⏳ needs your input (see below) | ❌ needs Xcode + Apple cert |
| Store listing content | ✅ drafted below | ✅ drafted below |
| Privacy policy | ✅ drafted below — **needs a real legal read before publishing** | same |
| Developer account | ❌ **you** create this | ❌ **you** create this |
| Submit for review | ❌ **you** submit | ❌ **you** submit |

## What's blocking each platform right now

**iOS**: Only Xcode's Command Line Tools are installed on this machine, not the
Xcode.app IDE — the Simulator and the ability to sign/archive/upload an app only
ship inside the full app, which is a ~40GB App Store download tied to your Apple
ID. I can't trigger that install headlessly. Once you've installed Xcode:
```
npm run cap:ios     # builds the web app, syncs, opens the Xcode project
```
From there I can pick this back up — build, run in Simulator, set up signing.

**Android**: Nothing's blocking a debug build (already proven working). For a
*release* build I stopped short of generating the signing keystore myself — see below.

## The Android release keystore — needs your decision

The upload keystore is the credential that permanently identifies Lawgic to Google
Play; losing it (with no backup) means you can never publish an update to the same
app listing again. I don't want to generate one with a password of my own choosing
and have that be the only record of it. Two ways to proceed:

1. **You pick the passwords**, tell me, and I generate it and wire up
   `android/app/build.gradle` signing config immediately — fastest path.
2. **You generate it yourself** with Android Studio's Build > Generate Signed
   Bundle/APK wizard (also lets Google Play App Signing manage the upload key for
   you afterward, which is Google's recommended setup and removes most of the
   "lose the keystore = game over" risk).

Either way: back the `.keystore` file and its passwords up somewhere durable
(password manager, not just this machine) before the first release build.

## Accounts you need to create (I cannot do this for you)

- **Google Play Console**: $25 one-time, console.play.google.com, needs a Google
  account + payment method + (for new developer accounts) identity verification,
  which can take a few days.
- **Apple Developer Program**: $99/year, developer.apple.com, needs an Apple ID +
  payment; verification can take up to 48 hours.

## Review considerations specific to this app

Both stores scrutinize apps that touch legal/medical advice, sensitive personal
data, or safety features more than average:

- Google Play's **Data Safety** form and Apple's **App Privacy** labels both need
  accurate disclosure of what's collected: phone numbers (OTP login), legal case
  details, government-ID-adjacent info depending on what users type into case
  descriptions, and location if you enable it for lawyer matching.
- The **DV Quick-Exit** feature is a strong signal of good intent, but also means
  reviewers may look closely — the in-app disclaimer ("AI-assisted legal
  information, not a substitute for a licensed advocate") should stay prominent
  in the app itself, not just the listing.
- If `access_status` gating means a reviewer can't get past a pending-approval
  screen, include a note + test account in the review notes (both consoles have a
  field for this) — same idea as giving a reviewer credentials to a gated app.

## Store listing (draft — edit freely)

**App name**: Lawgic — The Legal AId

**Short description** (Play Store, 80 chars max):
> AI legal help for India — case analysis, documents, lawyers, know your rights.

**Full description**:
> Lawgic is an AI-powered legal platform built for India. Describe your legal
> problem in plain language — in any of 22 Indian languages — and get a concrete
> action plan: which forum to approach, what to file, what it costs, and lawyers
> who can help.
>
> - **Case Analysis** — AI-assessed win probability, legal strategy, and relevant
>   statutes for your situation
> - **Document Generator** — 30+ court-ready templates, from legal notices to writ
>   petitions
> - **Legal Research** — search Indian statutes and case law
> - **Lawyer Marketplace** — get matched with verified advocates
> - **Free Legal Aid Check** — see in two minutes if you qualify for NALSA's
>   government-funded free legal aid program
> - **Know Your Rights** — free, shareable plain-language guides
>
> Free to start. This app provides AI-assisted legal information, not a
> substitute for advice from a licensed advocate.

**Category**: Business or Education (Play Store); Business or Reference (App Store)

**Keywords** (App Store, 100 chars): `legal,lawyer,india,law,document,case,rights,nalsa,advocate,court`

## Privacy policy (draft — needs a real legal review before you publish)

This is a starting draft, not legal advice, and not something to publish as-is —
have someone actually qualified look at it before it goes live, especially given
DPDP Act 2023 (India's data protection law) applies to this app's processing.

> **Privacy Policy for Lawgic ("the App")**
> Last updated: [date]
>
> Lawgic ("we", "us") provides AI-assisted legal information and document
> drafting for users in India. This policy explains what we collect and why.
>
> **What we collect**: account details (name, email, phone number), content you
> submit for analysis (case descriptions, documents you generate), OTP codes sent
> to your phone for login, and payment records for subscriptions/credits (we do
> not store card details — payments are processed by Razorpay/UPI).
>
> **How we use it**: to provide the service (AI case analysis, document
> generation, lawyer matching), to send OTP codes and deadline reminders, and to
> improve the product. Case content is sent to our AI providers (Groq, Anthropic)
> to generate responses — it is not used to train their models beyond their own
> standard data-use terms, which you should review independently.
>
> **What we don't do**: we don't sell your data. We don't share case content with
> third parties except the AI providers necessary to generate your response, and
> lawyers you explicitly choose to connect with.
>
> **Your rights**: you can request deletion of your account and associated data
> by contacting [support email]. Sensitive submissions (e.g. via the Quick Exit /
> domestic violence safety feature) are not treated differently in storage from
> other case data — if that matters to you, avoid entering identifying details
> you wouldn't want retained, and use Quick Exit to leave the app instantly if
> needed.
>
> **Data retention**: [fill in — e.g. "retained while your account is active,
> deleted within 90 days of account deletion"]
>
> **Contact**: [support email / physical business address — required by both
> stores]

Fill in the bracketed placeholders and get a real review before this goes live —
this is the single most important thing not to rubber-stamp given what this app's
users are trusting it with.
