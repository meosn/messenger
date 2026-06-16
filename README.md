# Messenger

A lightweight real-time messenger project with two parts:

- `backend/` - FastAPI backend with WebSocket-based signaling and chat delivery
- `messenger_client/` - SwiftUI client for composing and viewing messages

## Backend

The backend exposes:

- `GET /` health endpoint
- `WS /socket/{user_id}` WebSocket channel for chat and signaling

## iOS Client

The SwiftUI app provides a simple chat UI with message bubbles and scrolling behavior.

## Run

Backend:

```bash
pip install fastapi uvicorn pydantic
uvicorn backend.main:app --reload
```

Client:

```bash
open MessengerClient.xcodeproj
```

## Notes

- The iOS target now uses a clean, consistent project name.
- The backend no longer prints noisy debug output on import.
