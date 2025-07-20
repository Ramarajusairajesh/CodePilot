# Coding Agent Platform

## Overview
A scalable, secure coding agent platform with sandboxed execution, GUI automation, and orchestration. Each job runs in an isolated Docker container with a live GUI (VNC/NoVNC), Jupyter, and REST APIs for shell, code, xdot, and filesystem control.

## Architecture
- **Orchestrator**: FastAPI server to schedule and track jobs, launches agent containers.
- **Agent**: Docker container with Xvfb, VNC, NoVNC, Jupyter, and agent server (Flask).
- **Context Management**: File-based, prunes old entries for >1M token support.

## Setup

### 1. Build Agent Docker Image
```sh
cd agent
docker build -t coding-agent .
```

### 2. Run Orchestrator
```sh
cd orchestrator
pip install fastapi uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

### 3. (Dev) Run Agent Directly
```sh
cd agent
docker run -it -p 5901:5901 -p 8080:8080 -p 5000:5000 -p 8888:8888 coding-agent
```

## Usage

### Schedule a Job
```sh
curl -X POST http://localhost:9000/schedule -H 'Content-Type: application/json' -d '{"task": "Build me a todo app in React"}'
```
Response: `{ "job_id": "..." }`

### Check Status
```sh
curl http://localhost:9000/status/<job_id>
```

### Accessing the Agent
- **VNC**: Connect to `localhost:5901` (passwordless)
- **NoVNC**: Open `http://localhost:8080/vnc.html?host=localhost&port=8080`
- **Jupyter**: Open `http://localhost:8888` (token in logs)

### Agent API Endpoints
- `POST /shell` `{ "cmd": "ls -la" }`
- `POST /code` `{ "lang": "python", "code": "output = 2+2" }`
- `POST /xdot` `{ "cmd": "mousemove 100 100 click 1" }`
- `POST /fs` `{ "action": "create", "path": "foo.txt", "content": "bar" }`

## Security & Scalability
- Each job runs in an isolated Docker container for security and resource control.
- Orchestrator can be scaled horizontally (see k8s job below).

--- 