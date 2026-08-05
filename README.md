# BragStack

> **Don’t just claim your impact. Stack the proof.**

BragStack is a career-proof platform that helps people document their work, preserve evidence of their contributions, and turn real accomplishments into useful career materials.

Users can record wins throughout the year, organize measurable impact, publish selected accomplishments, and maintain a portable professional record.

BragStack is evolving around a core concept called **Impact Receipts**: structured, evidence-backed records showing what someone contributed, what changed, and why it mattered.

---

## Why BragStack?

Important work is often forgotten, overlooked, or difficult to reconstruct later.

People regularly struggle to remember specific examples when preparing for:

- Promotions
- Performance reviews
- Interviews
- One-on-one meetings
- Client reports
- Résumé updates
- Portfolio updates
- Career transitions

BragStack helps users capture accomplishments while the details are still fresh.

Every win can be documented. Significant wins can become **Impact Receipts**.

---

## Who BragStack Is For

### Promotions

Walk into promotion conversations with organized proof of impact, growth, ownership, and added responsibilities.

### Interviews

Turn real accomplishments into confident interview stories instead of trying to remember examples under pressure.

### Performance Reviews

Build a review throughout the year instead of reconstructing twelve months of work the night before.

### One-on-One Meetings

Bring wins, blockers, lessons, and progress into conversations with managers.

### Trainers and Clients

Document milestones, completed goals, progress, and measurable results over time.

### Freelancers and Consultants

Turn completed projects into client updates, case studies, testimonials, and proof of value.

### Students and Career Changers

Track projects, certifications, new skills, and portfolio evidence while developing a career.

### Creators and Founders

Capture launches, experiments, customer wins, audience growth, partnerships, and business milestones.

---

## Current Features

### Accounts and Profiles

- User registration and login
- JWT-based authentication
- User-owned private data
- Editable professional profiles
- Professional headline and biography
- Location
- GitHub, portfolio, and résumé links
- Unique public profile URLs

### Accomplishment Tracking

- Create brag entries
- Edit existing entries
- Delete entries
- Categorize accomplishments
- Add entry dates and entry types
- Record situation, action, impact, and lessons
- Add skill tags
- Mark entries as public or private
- Generate résumé-style accomplishment bullets

### Reports and Summaries

- Weekly accomplishment reports
- Skill-tag summaries
- Category summaries
- Recent accomplishment dashboard

### Public Career Proof

- Public BragStack profiles
- Public-only accomplishment filtering
- Shareable profile URLs
- Public and private visibility controls

### Product Experience

- Marketing landing page
- Responsive React interface
- Docker Compose development environment
- FastAPI interactive API documentation

---

## Impact Receipts

Impact Receipts are the planned core feature of BragStack.

An Impact Receipt is a structured record of a meaningful contribution.

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

Confirmed by:
✓ Collaborator
✓ Manager
```

Impact Receipts will help users document:

- What happened
- What they personally contributed
- What changed because of the work
- Which skills were demonstrated
- What evidence supports the claim
- Who else contributed
- Who confirmed the contribution

---

## Impact Receipt Trust Signals

Impact Receipts will support progressive trust signals.

| Trust signal | Meaning |
|---|---|
| Self-documented | Entered by the owner |
| Evidence-linked | Includes tickets, documents, pull requests, feedback, or other evidence |
| Collaborator-confirmed | A teammate or collaborator confirms the contribution |
| Stakeholder-verified | A manager, client, instructor, trainer, or other stakeholder verifies the claim |
| Organization-issued | An organization formally recognizes the accomplishment |

These signals will remain separate so BragStack can clearly communicate what has and has not been verified.

---

## Shared Credit

Real work is collaborative.

BragStack will allow multiple contributors to receive accurate credit for different parts of the same outcome.

```text
Project outcome:
Successful production recovery

Tee:
Diagnosed the production failures

Jordan:
Implemented and tested the backend fix

Maria:
Coordinated the customer rollout

Alex:
Documented the recovery process
```

Each contributor can receive a related Impact Receipt without claiming the entire project.

---

## Product Model

BragStack follows a simple product flow:

```text
Brag Entry
    ↓
Impact Receipt
    ↓
Career Output
```

### Brag Entry

A fast way to record everyday wins, progress, lessons, and responsibilities.

### Impact Receipt

A significant accomplishment enhanced with evidence, contribution details, shared credit, and verification.

### Career Output

Impact Receipts can later power:

- Promotion packets
- Performance-review summaries
- Interview stories
- Résumé bullets
- Client reports
- Case studies
- Public proof cards
- Embedded portfolios
- Team impact dashboards

---

## Technology Stack

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

### Data and Infrastructure

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
│   │   └── PublicBragPage.jsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Run BragStack Locally

Make sure Docker is installed and running.

From the project root:

```bash
docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

Open the frontend:

```text
http://localhost:5173
```

Open the API documentation:

```text
http://localhost:8000/docs
```

---

## Development Commands

### Build the Frontend

```bash
docker compose exec frontend npm run build
```

### Run Backend Tests

```bash
docker compose exec api pytest
```

### Restart the API

```bash
docker compose restart api
```

### Stop BragStack

```bash
docker compose down
```

### Remove Containers and Local MongoDB Data

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
| `PATCH` | `/auth/me/profile` | Update the authenticated user’s profile |

### Accomplishments

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/entries` | Create an accomplishment |
| `GET` | `/entries` | List the authenticated user’s accomplishments |
| `GET` | `/entries/{entry_id}` | View one accomplishment |
| `PUT` | `/entries/{entry_id}` | Update an accomplishment |
| `DELETE` | `/entries/{entry_id}` | Delete an accomplishment |
| `GET` | `/entries/reports/weekly` | Generate a weekly report |
| `GET` | `/entries/tags/summary` | Summarize skill tags |
| `GET` | `/entries/categories/summary` | Summarize categories |

### Public Profiles

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/public/brag/{slug}` | View public accomplishments |
| `GET` | `/public/brag/{slug}/profile` | View public profile information |
| `GET` | `/public/brag/{slug}/reports/weekly` | View the public weekly report |
| `GET` | `/public/brag/{slug}/tags/summary` | View public skill summaries |
| `GET` | `/public/brag/{slug}/categories/summary` | View public category summaries |

---

## Current Development Milestone

The current milestone is **Impact Receipts V1**.

Planned V1 work:

- [ ] Complete editable-profile persistence testing
- [ ] Display saved profile information on public profiles
- [ ] Remove remaining hardcoded public-profile information
- [ ] Create the first Impact Receipt backend model
- [ ] Convert an existing brag entry into an Impact Receipt
- [ ] Add a **Create Impact Receipt** action to entries
- [ ] Display the first Impact Receipt card
- [ ] Add receipt visibility controls
- [ ] Add receipt creation and update timestamps

---

## Roadmap

### Impact Receipts V1

- Structured accomplishment records
- Individual contribution details
- Results and measurable impact
- Skills backed by accomplishments
- Public and private receipt cards

### Evidence

- Evidence links
- GitHub pull requests
- Jira and Zendesk tickets
- Documentation
- Customer feedback
- File attachments

### Shared Credit and Confirmation

- Contributor invitations
- Individual contribution roles
- Collaborator confirmation
- Stakeholder verification
- Verification history
- Revocation and correction workflows

### Career Outputs

- Review Packet Generator
- Promotion packets
- Interview-story generation
- Résumé exports
- Client impact reports
- Markdown and PDF exports

### Teams and Organizations

- Organizations
- Teams
- Invitations
- Member roles
- Manager workflows
- Team impact dashboards
- Custom review templates

### Integrations and Enterprise

- GitHub integration
- Jira integration
- Zendesk integration
- Slack integration
- Compact iframe embeds
- SSO
- Audit logs
- Enterprise permissions
- Verifiable credentials

---

## Product Principles

BragStack is being designed around several principles:

1. **Employees control their career proof.**
2. **Sensitive workplace evidence should remain private by default.**
3. **Imported activity should require user approval.**
4. **Shared work should receive shared credit.**
5. **Verification should clearly state what was confirmed.**
6. **BragStack should support existing HR systems instead of forcing companies to replace them.**
7. **The product should reveal overlooked work without becoming workplace surveillance.**

---

## Vision

BragStack is where work becomes portable, shared-credit, verifiable career proof.

The long-term goal is to give every person a living record of their contributions while helping organizations recognize impact that traditional performance systems often miss.

---

## Author

Built by Tee as a SaaS product focused on career proof, workplace impact, backend development, Docker, MongoDB, and modern product engineering.
