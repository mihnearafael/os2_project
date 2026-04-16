# OS File Integrity Monitor

A real-time, agent-based File Integrity Monitoring (FIM) system built with Django and Python. It detects unauthorized changes to sensitive files and reports them to a centralized web dashboard as they happen.

## Overview

This project is split into two decoupled parts:

- `monitor.py`: a lightweight FIM agent that watches the local filesystem for file events such as create, modify, and delete.
- `Django dashboard`: a web application that receives alerts through a webhook, stores them, and renders them in a security-focused console.

The result is a simple producer-consumer pipeline for monitoring critical files and reviewing events in near real time.

## Features

- Real-time detection of file tampering
- Content inspection with a snapshot of file contents on create or modify events
- Noise filtering for common temporary editor artifacts such as JetBrains safe-write files, `~` backups, and `.tmp` files
- Self-refreshing dashboard with clear visual alerting
- Persistent alert history stored in SQLite for later review

## Architecture

The system follows a producer-consumer model:

1. The FIM agent watches `./sensitive_files` using `watchdog`.
2. When a file event occurs, the agent builds a JSON alert payload.
3. The payload is sent with an HTTP `POST` request to the Django webhook endpoint.
4. Django stores the alert in the database and displays it on the dashboard.

```text
┌─────────────────┐    JSON over HTTP    ┌──────────────────────┐
│  monitor.py     │ ───────────────────▶ │ Django webhook       │
│  FIM agent      │                      │ /alerts/webhook/     │
└─────────────────┘                      └──────────┬───────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────┐
                                          │ SQLite alert store   │
                                          └──────────┬───────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────┐
                                          │ Dashboard UI         │
                                          │ /alerts/             │
                                          └──────────────────────┘
```

## Tech Stack

- Python 3
- Django
- Watchdog
- Requests
- SQLite

## Installation

### 1. Prerequisites

- Python `3.10+`
- `pipenv` recommended, or plain `pip`

### 2. Install dependencies

Using `pipenv`:

```bash
pipenv install django watchdog requests
```

Using `pip`:

```bash
pip install django watchdog requests
```

### 3. Initialize the database

```bash
python manage.py makemigrations
python manage.py migrate
```

## How To Run

Run the dashboard and the monitoring agent in two separate terminals.

### Terminal 1: Start the Django dashboard

```bash
python manage.py runserver
```

Open:

- Dashboard: `http://127.0.0.1:8000/alerts/`
- Webhook endpoint: `http://127.0.0.1:8000/alerts/webhook/`

### Terminal 2: Start the FIM agent

```bash
python monitor.py
```

The agent will watch the `./sensitive_files` directory. If that folder does not exist yet, it is created automatically at startup.

## Testing The System

1. Open the `sensitive_files/` directory.
2. Create, edit, or delete a file from your terminal or IDE.
3. Watch the agent log a sent alert in the terminal.
4. Open the dashboard and confirm the new alert appears automatically.

Each alert includes:

- Event type
- Target file path
- Timestamp
- A content preview for created or modified files

## Project Structure

```text
.
├── manage.py
├── monitor.py
├── sensitive_files/
├── db.sqlite3
├── os2_fim/
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── alerts/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── migrations/
    └── templates/
        └── alerts/
            └── dashboard.html
```

## Security Note

The webhook receiver uses `@csrf_exempt` so the external monitoring agent can post alerts directly to Django.

That is acceptable for local development, but in a production deployment this endpoint should be protected with a stronger authentication mechanism such as:

- API keys
- Token-based authentication
- Network allowlisting or reverse-proxy restrictions

## Use Cases

- Monitoring configuration files
- Watching application secrets directories
- Detecting tampering during local security demos or labs
- Teaching the producer-consumer pattern in a practical security project
