# BragStack

> **Your work deserves receipts. Capture what you did. Prove the impact. Build the packet.**

BragStack is a **career evidence system for people in any profession**. It helps people turn day-to-day work into portable proof they can reuse for reviews, promotions, interviews, résumés, portfolios, client conversations, and career transitions.

BragStack is intentionally not built around one profession. A teacher, nurse, warehouse lead, stylist, salesperson, mechanic, nonprofit coordinator, designer, student, manager, developer, or public-service worker should all be able to use the same core model:

```text
Accomplishment
    ↓
Contribution + Result
    ↓
Impact Receipt
    ↓
Evidence + Skills + Shared Credit + Recognition
    ↓
Career Report / Proof Profile / Professional Packet
```

The product focuses on universal career concepts:

- accomplishments
- contributions
- results
- evidence
- skills
- recognition
- goals and growth
- measurable impact
- shared credit

No profession-specific field is required for the core evidence model.

---

## Why BragStack exists

Important work is easy to forget and surprisingly hard to reconstruct later.

BragStack lets users record accomplishments while they are fresh, turn meaningful wins into structured **Impact Receipts**, and assemble that evidence into professional artifacts when an opportunity appears.

Instead of saying:

> “I know I did a lot this year…”

BragStack helps a user show:

- what happened
- what they personally contributed
- what changed
- what skills they demonstrated
- what evidence supports the claim
- who shared credit
- what has or has not been independently confirmed

---

## Impact Receipts

An **Impact Receipt** is BragStack's structured proof record.

It can contain:

- accomplishment
- specific contribution
- result or measurable impact
- supporting evidence
- demonstrated skills
- shared credit
- confirmations / recognition
- trust signals
- public/private visibility

Example:

```text
IMPACT RECEIPT

Accomplishment:
Improved family conference participation

Contribution:
Redesigned reminder messaging and coordinated multilingual outreach

Result:
Increased participation by 24% across the grade level

Evidence:
✓ Attendance summary
✓ Family feedback

Skills:
Communication · Family Engagement · Program Coordination

Recognition:
✓ School leader confirmed contribution
```

The same structure works for clinical care, teaching, sales, operations, trades, creative work, customer service, management, technology, public service, and more.

---

## Product surfaces

### Accomplishment tracking

- create, edit, and delete accomplishments
- work dates and career categories
- skill tags
- situation/action/impact/lessons fields
- reusable résumé-style bullets
- public/private visibility
- paginated accomplishment library

### Impact Receipts

- convert accomplishments into structured proof
- separate contribution from result
- attach evidence metadata
- record skills and shared credit
- track confirmations and trust signals
- private-by-default evidence behavior

### Reports Hub

- weekly career reports
- all-time career summaries
- custom date ranges
- accomplishment and evidence metrics
- skill/category summaries
- quantified-result tracking
- career highlights
- résumé bullet output
- Markdown copy/export

### Proof Profile

- shareable public career-proof page
- public-only accomplishments and Impact Receipts
- career analytics
- evidence-aware skill/category summaries
- public activity trends
- privacy-safe pagination

### Performance Review Packet

A Pro-grade, paper-first professional dossier generated from real BragStack evidence.

Includes:

- cover
- executive scorecard
- impact analytics
- signature accomplishments
- measurable results
- skills and growth
- contribution and recognition
- Impact Receipt appendix
- evidence index
- review summary
- true server-generated PDF export

### Promotion Packet

Reuses the same evidence engine for progression conversations.

Includes:

- target role / progression context
- demonstrated impact
- scope and ownership
- measurable outcomes
- growth and capabilities
- verified recognition
- evidence gaps / ways to strengthen the case
- direct PDF export

BragStack does **not** assign an opaque promotion-readiness score or make an employment decision.

### Interview Packet

The Interview Packet turns **user-selected accomplishments** into interview preparation material.

It is designed to:

- let users choose the stories they actually want to discuss
- surface contribution, result, skills, and proof status
- generate preparation questions when a story is missing context
- keep private evidence references out of the packet unless explicitly included
- avoid inventing STAR details, metrics, or claims
- export a professional interview-prep PDF

---

## Trust and privacy principles

BragStack is built around a few non-negotiable rules:

1. **Users control their career proof.**
2. **Sensitive workplace evidence stays private by default.**
3. **Imported activity should require user approval.**
4. **Shared work deserves shared credit.**
5. **Verification must clearly state what was actually confirmed.**
6. **BragStack should complement existing HR systems, not require replacing them.**
7. **Career visibility should not become workplace surveillance.**
8. **Generated packets must not invent facts, scores, outcomes, or evidence.**

---

## Plans foundation

BragStack currently has entitlement foundations for:

- **Free** — core career proof
- **Pro** — advanced reports, packets, PDF export, integrations foundation
- **Team** — shared review workflows and manager/team features
- **Enterprise** — organization analytics, governance, SSO/audit foundations

Pricing and billing implementation can evolve independently from the entitlement model.

---

## Architecture

```text
React + Vite frontend
        │
        ▼
FastAPI REST API
        │
        ▼
MongoDB
```

### Frontend

- React
- Vite
- Axios
- Lucide React
- CSS

### Backend

- Python
- FastAPI
- Pydantic
- PyMongo
- JWT authentication
- ReportLab PDF generation

### Infrastructure

- Docker
- Docker Compose
- MongoDB
- GitHub Actions
- Swagger / OpenAPI

Both backend tests and frontend lint/production builds are gated through GitHub Actions.

---

## Run locally

### Requirements

- Docker
- Docker Compose

From the project root:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

Frontend:

```text
http://localhost:5173
```

API documentation:

```text
http://localhost:8000/docs
```

### Development checks

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
docker compose exec api pytest
```

Stop the stack:

```bash
docker compose down
```

---

## Core API areas

### Authentication and profiles

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PATCH /auth/me/profile`

### Accomplishments

- `POST /entries`
- `GET /entries`
- `GET /entries/{entry_id}`
- `PUT /entries/{entry_id}`
- `DELETE /entries/{entry_id}`

### Impact Receipts

- `POST /impact-receipts/from-entry/{entry_id}`
- `GET /impact-receipts`
- `PATCH /impact-receipts/{receipt_id}`

### Packets

- `GET /packets/performance-review`
- `GET /packets/performance-review.pdf`
- `GET /packets/promotion`
- `GET /packets/promotion.pdf`
- `GET /packets/interview`
- `GET /packets/interview.pdf`

---

## Roadmap

Current post-V1 directions include:

- cross-career packet regression fixtures
- branded packet themes
- selective packet sections
- packet sharing + expiration controls
- accomplishment pinning/reordering
- packet-only notes and annotations
- certification/licensure packet
- stronger manager recognition and review-cycle workflows
- organization skill intelligence
- HRIS and enterprise integrations
- SSO, SCIM, audit, retention, and RBAC expansion

---

## Vision

**BragStack is a portable record of real work.**

What happened. What you contributed. What changed. What proves it. What you learned. And how that evidence can move with you throughout your career.

The long-term goal is simple: make meaningful work easier to remember, explain, verify, and carry forward—no matter what kind of work you do.
