# external_ha_server

A lightweight Flask-based proxy that exposes select Home Assistant endpoints (states, events, services) via a secure, token-based external REST API.

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Running the Server](#running-the-server)  
- [API Usage](#api-usage)  
  - [Authentication](#authentication)  
  - [Endpoints](#endpoints)  
- [Advanced Topics](#advanced-topics)  
  - [CORS and Reverse Proxies](#cors-and-reverse-proxies)  
  - [Deployment](#deployment)  
  - [Logging & Monitoring](#logging--monitoring)  
- [Testing](#testing)  
- [Contribution](#contribution)  
- [License](#license)  

---

## Features

- **Selective Proxying**: Read states, fire events, and call services in Home Assistant without exposing your full instance.  
- **Token-Based Security**: Leverages Home Assistant long-lived access tokens for all requests.  
- **Lightweight**: Minimal dependencies; built on Flask.  
- **Configurable**: Enable or disable specific API groups (states, events, services).  
- **Extensible**: Easily add custom endpoints or middleware.

## Architecture

1. **Flask App** (`app.py`)  
2. **Configuration Loader** (`config.py`) – reads `.env` or environment variables  
3. **Proxy Logic** (`proxy.py`) – forwards requests to HA while preserving paths & queries  
4. **Error Handling** – standardized JSON errors  
5. **Optional Middleware** – rate limiting, logging, additional auth layers

## Prerequisites

- Python 3.8+  
- A running Home Assistant instance  
- A Home Assistant long-lived access token  
- (Optional) Reverse proxy (e.g., Nginx) for TLS termination

## Installation

```bash
git clone https://github.com/n9vo/external_ha_server.git
cd external_ha_server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy and edit the example environment file:

```bash
cp .env.example .env
```

```dotenv
HA_BASE_URL=https://homeassistant.local:8123
HA_TOKEN=YOUR_LONG_LIVED_TOKEN
ENABLED_GROUPS=states,events,services
CORS_ORIGINS=*
FLASK_SECRET_KEY=change_this_to_a_random_secret
```

- **HA_BASE_URL**: Full API URL (include `http://`/`https://`).  
- **ENABLED_GROUPS**: Comma-separated subset of `states,events,services`.  
- **CORS_ORIGINS**: Domains allowed via CORS (`*` for all).  

## Running the Server

### Development

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Production (Gunicorn)

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### Docker

```bash
docker build -t external_ha_server .
docker run -d \
  --name ext-ha \
  --env-file .env \
  -p 5000:5000 \
  external_ha_server
```

## API Usage

All requests must include:

```
Authorization: Bearer <HA_TOKEN>
```

### Endpoints

#### States

- **GET** `/api/states`  
  Returns all entity states.

- **GET** `/api/states/<entity_id>`  
  Returns state & attributes for `entity_id`.

#### Events

- **GET** `/api/events`  
  Lists event types.

- **POST** `/api/events/<event_type>`  
  Fires an event.  
  ```json
  {
    "event": { "key": "value", … }
  }
  ```

#### Services

- **GET** `/api/services`  
  Lists all services.

- **POST** `/api/services/<domain>/<service>`  
  Calls a service.  
  ```json
  {
    "entity_id": "light.living_room",
    …
  }
  ```

## Advanced Topics

### CORS and Reverse Proxies

- Configure `CORS_ORIGINS` for direct exposure.  
- Terminate TLS in Nginx or Traefik as needed.

### Deployment

- Use Gunicorn with multiple workers.  
- Place behind Nginx for SSL, buffering, and hosting.

### Logging & Monitoring

- Logs to stdout by default.  
- Add Python `logging` config in `app.py` for file/external sinks.  
- Health check endpoint:  
  ```
  GET /health → HTTP 200 if HA reachable
  ```

## Testing

1. **Unit tests** (if provided)  
   ```bash
   pytest tests/
   ```
2. **Manual**  
   ```bash
   curl -H "Authorization: Bearer $HA_TOKEN" \
        http://localhost:5000/api/states
   ```

## Contribution

1. Fork & clone  
2. `git checkout -b feature/foo`  
3. Code, commit, push  
4. Open a Pull Request  

Adhere to PEP 8, include tests, and update this README for new behavior.

## License

[MIT License](LICENSE)
