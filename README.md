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