# BragStack

BragStack is a SaaS-style career proof tracker that helps technical workers log wins, track skills, generate resume-ready bullets, and summarize weekly progress.

It is built with FastAPI, MongoDB, Docker, and Docker Compose, with Kubernetes support planned as the project grows.

## Why BragStack?

Technical workers often solve meaningful problems every day but forget the details when it is time to update a resume, prepare for interviews, ask for a raise, or explain their impact.

BragStack helps users turn daily work into career evidence.

## Current Features

- Create brag entries
- List all brag entries
- View a single brag entry
- Update brag entries
- Delete brag entries
- Generate resume-style bullets
- Generate weekly progress reports
- Track categories and skill tags
- Run locally with Docker Compose
- Store data in MongoDB

## Tech Stack

- Python
- FastAPI
- MongoDB
- PyMongo
- Docker
- Docker Compose
- Swagger / OpenAPI

## Project Structure

```text
bragstack/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── README.md
└── .gitignore
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/entries` | Create a brag entry |
| `GET` | `/entries` | List all brag entries |
| `GET` | `/entries/{entry_id}` | View one brag entry |
| `PUT` | `/entries/{entry_id}` | Update a brag entry |
| `DELETE` | `/entries/{entry_id}` | Delete a brag entry |
| `GET` | `/entries/reports/weekly` | Generate a weekly progress report |

## Example Brag Entry

```json
{
  "title": "Debugged Docker Compose networking issue",
  "category": "Docker",
  "situation": "A service could not connect to MongoDB inside a Docker Compose environment.",
  "action": "checked container logs, inspected the Compose network, and verified the MongoDB service hostname",
  "impact": "identified that the app was using localhost instead of the Compose service name",
  "lesson": "Inside Docker Compose, containers should use service names for DNS resolution.",
  "tags": ["Docker", "Compose", "Networking", "MongoDB"]
}
```

## Example Generated Resume Bullet

```text
Resolved docker issue involving Docker, Compose, Networking, MongoDB by checked container logs, inspected the Compose network, and verified the MongoDB service hostname Result: identified that the app was using localhost instead of the Compose service name
```

## Run Locally with Docker Compose

Make sure Docker Desktop is running.

From the project root:

```bash
docker compose up --build
```

Then open the API docs:

```text
http://localhost:8000/docs
```

## Stop the App

```bash
docker compose down
```

To remove MongoDB data too:

```bash
docker compose down -v
```

## Environment Variables

The backend uses the following environment variable:

| Variable | Description | Default |
|---|---|---|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |

In Docker Compose, this is set to:

```text
mongodb://mongo:27017
```

## DevOps Concepts Demonstrated

This project demonstrates:

- Building a FastAPI backend
- Connecting FastAPI to MongoDB
- Creating REST API endpoints
- Using Dockerfiles to containerize an application
- Running a multi-container environment with Docker Compose
- Connecting services through Docker Compose networking
- Persisting MongoDB data with Docker volumes
- Testing API behavior through Swagger/OpenAPI
- Using timezone-aware UTC datetime values
- Structuring a backend project for future SaaS growth

## Roadmap

Planned features:

- React or Next.js frontend
- User authentication
- Skill/tag summary dashboard
- Monthly reports
- STAR interview story generator
- AI-assisted resume bullet generation
- Export entries to Markdown or PDF
- Kubernetes manifests
- GitHub Actions CI workflow
- Deployment to a cloud environment

## Future Kubernetes Goals

BragStack will eventually include Kubernetes manifests for:

- Backend Deployment
- Backend Service
- MongoDB Deployment
- MongoDB Service
- ConfigMap
- Secret
- Ingress
- Health checks

## Author

Built by Tee as a portfolio SaaS project to showcase backend development, Docker, MongoDB, and future Kubernetes/DevOps skills.
