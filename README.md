# BragStack

> **Don’t just claim your impact. Stack the proof.**

BragStack is an evidence-backed career-proof platform for turning day-to-day work into portable, reusable proof of impact.

Instead of trying to reconstruct a year of work before a performance review or interview, users can record accomplishments as they happen, convert meaningful wins into **Impact Receipts**, and generate career reports they can reuse for reviews, résumés, interviews, portfolios, and promotion conversations.

## What makes BragStack different

Most career trackers stop at notes or résumé bullets. BragStack adds a trust layer.

```text
Brag Entry
    ↓
Impact Receipt
    ↓
Evidence + Shared Credit + Trust Signals
    ↓
Career Report / Public Proof
```

An **Impact Receipt** captures:

- the accomplishment
- the owner’s specific contribution
- the result or measurable impact
- supporting evidence
- demonstrated skills
- shared credit for collaborators
- confirmation and trust signals
- public/private visibility

That turns a claim like “improved reliability” into a structured record that can show what happened, who did what, what changed, and what supports the claim.

---

## BragStack V1

BragStack V1 includes the complete core flow from accomplishment capture to career output.

### Accounts and Profiles

- User registration and login
- JWT authentication
- User-owned private data
- Editable professional profiles
- Professional headline, bio, and location
- GitHub, portfolio, and résumé links
- Unique public profile URLs

### Accomplishment Tracking

- Create, edit, and delete brag entries
- Record situation, action, impact, and lessons
- Categorize accomplishments
- Add work dates and entry types
- Add skill tags
- Public/private visibility controls
- Generate reusable résumé-style bullets

### Impact Receipts

- Convert an existing accomplishment into an Impact Receipt
- Store contribution and result separately
- Add evidence metadata
- Track demonstrated skills
- Record shared credit
- Track confirmations and trust signals
- Public/private receipt visibility
- Creation and update timestamps
- Public receipt data excludes private evidence by default

### Reports Hub

- Weekly career reports
- All-time career summaries
- Custom date-range reports
- Combined accomplishment and Impact Receipt metrics
- Evidence and confirmation counts
- Skill and category summaries
- Quantified-result tracking
- Career highlights
- Reusable résumé bullets
- Highlight search by title, category, skill, result, or trust signal
- Copy résumé bullets
- Copy full reports as Markdown
- Download portable Markdown reports

### Public Career Proof

- Shareable public BragStack profile
- Public-only accomplishment filtering
- Public Impact Receipts
- Public skill/category summaries
- Privacy controls that keep non-public evidence out of public responses

---

## Impact Receipt Example

```text
IMPACT RECEIPT

Accomplishment:
Prevented a recurring Docker DNS outage

My contribution:
Identified the networking regression and created the fix

Result:
Reduced repeat escalations by 35%

Evidence:
✓ Support incident
✓ Pull request
✓ Internal documentation
✓ Customer feedback

Skills demonstrated:
Docker Networking · Troubleshooting · Incident Leadership

Credit:
Tee — Root-cause analysis
Jordan — Testing
Maria — Deployment

Trust signals:
✓ Self-documented
✓ Evidence-linked
✓ Collaborator-confirmed
```

### Trust signals

| Trust signal | Meaning |
|---|---|
| Self-documented | Entered by the owner |
| Evidence-linked | Includes supporting evidence |
| Collaborator-confirmed | A collaborator confirms the contribution |
| Stakeholder-verified | A manager, client, instructor, or stakeholder verifies it |
| Organization-issued | An organization formally recognizes the accomplishment |

Trust signals remain separate so BragStack can clearly communicate what has and has not been independently verified.

---

## Why this matters

Important work is easy to forget and hard to reconstruct later. BragStack is designed for people preparing for:

- promotions
- performance reviews
- interviews
- one-on-one meetings
- résumé updates
- portfolio updates
- consulting/client reports
- career transitions

It is also useful for students, career changers, freelancers, founders, and creators who need a durable record of projects, milestones, skills, and outcomes.

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

The application runs locally through Docker Compose and uses GitHub Actions for automated backend validation.

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

### Infrastructure

- MongoDB
- Docker
- Docker Compose
- GitHub Actions
- Swagger / OpenAPI

---

## Project Structure

```text
bragstack/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── auth.py
│   │   ├── auth_routes.py
│   │   ├── impact_receipt_routes.py
│   │   ├── reports_routes.py
│   │   └── public_slug_routes.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── api.js
│   │   ├── AuthPage.jsx
│   │   ├── LandingPage.jsx
│   │   ├── PublicBragPage.jsx
│   │   └── ReportsPage.jsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

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

Open the frontend:

```text
http://localhost:5173
```

Open interactive API documentation:

```text
http://localhost:8000/docs
```

### Development commands

Build the frontend:

```bash
docker compose exec frontend npm run build
```

Run frontend linting:

```bash
docker compose exec frontend npm run lint
```

Run backend tests:

```bash
docker compose exec api pytest
```

Stop BragStack:

```bash
docker compose down
```

Remove containers and local MongoDB data:

```bash
docker compose down -v
```

---

## API Highlights

### Authentication and Profiles

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Log in |
| `GET` | `/auth/me` | Get the authenticated user |
| `PATCH` | `/auth/me/profile` | Update the authenticated profile |

### Accomplishments

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/entries` | Create an accomplishment |
| `GET` | `/entries` | List accomplishments |
| `GET` | `/entries/{entry_id}` | View one accomplishment |
| `PUT` | `/entries/{entry_id}` | Update an accomplishment |
| `DELETE` | `/entries/{entry_id}` | Delete an accomplishment |

### Impact Receipts

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/impact-receipts/from-entry/{entry_id}` | Convert an entry into an Impact Receipt |
| `GET` | `/impact-receipts` | List owned Impact Receipts |
| `PATCH` | `/impact-receipts/{receipt_id}` | Update an Impact Receipt |

### Reports

The Reports Hub exposes authenticated weekly, all-time, and custom-period career reporting endpoints used by `/app/reports`.

### Public Profiles

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/public/brag/{slug}` | View public accomplishments |
| `GET` | `/public/brag/{slug}/profile` | View public profile information |
| `GET` | `/public/brag/{slug}/reports/weekly` | View public weekly report |
| `GET` | `/public/brag/{slug}/tags/summary` | View public skill summaries |
| `GET` | `/public/brag/{slug}/categories/summary` | View public category summaries |

---

## Privacy and product principles

BragStack is designed around a few non-negotiable ideas:

1. **Users control their career proof.**
2. **Sensitive workplace evidence stays private by default.**
3. **Imported activity should require user approval.**
4. **Shared work deserves shared credit.**
5. **Verification must clearly state what was actually confirmed.**
6. **BragStack should complement existing HR systems, not require replacing them.**
7. **Career visibility should not become workplace surveillance.**

---

## V1 status

### Complete

- [x] Authentication and private user data
- [x] Editable public profiles
- [x] Accomplishment CRUD
- [x] Public/private accomplishment controls
- [x] Impact Receipts V1
- [x] Evidence metadata and shared credit model
- [x] Trust-signal model
- [x] Public receipt privacy controls
- [x] Reports Hub V1
- [x] Weekly, all-time, and custom reports
- [x] Résumé bullet output
- [x] Markdown report export
- [x] Report highlight search
- [x] Automated backend coverage for reports, profiles, receipt visibility, and public privacy

### Future roadmap

These are deliberate post-V1 extensions, not unfinished V1 requirements:

- richer Impact Receipt editing UX
- direct GitHub/Jira/Zendesk integrations
- collaborator invitations and confirmation workflows
- review and promotion packet generators
- PDF export
- organizations and teams
- manager workflows and team impact dashboards
- SSO, audit logs, and enterprise permissions
- verifiable credentials

---

## Vision

BragStack is a portable record of real work: what happened, what you contributed, what changed, what proves it, and how that work can be reused throughout your career.

The long-term goal is simple: make meaningful work easier to remember, explain, verify, and carry forward.

---

## Author

Built by Tee as a SaaS product focused on career proof, workplace impact, backend development, Docker, MongoDB, React, FastAPI, and modern product engineering.
