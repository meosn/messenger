from pydantic import BaseModel
from datetime import datetime, timezone
from .connections import manager
from .models import SignalMessage

async def handle_chat(msg: SignalMessage) -> None:
    payload = msg.payload or {}
    text = payload.get("text")
    if not text:
        return
    timestamp = datetime.now(timezone.utc).isoformat()
    payload["timestap"] = timestamp
    msg.payload = payload
    if manager.get(msg.to_id):
        await manager.send_to_user(msg.to_id, msg.model_dump_json())
        print(f"[CHAT] {msg.from_id} → {msg.to_id}: {text}")
    else:
        print(f"[CHAT] {msg.to_id} офлайн, сообщение не доставлено: {text}")