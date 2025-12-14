import json
from fastapi import WebSocket
from .models import SignalMessage
from .connections import manager

async def handle_signal(data:str, sender_socket: WebSocket):
    msg = SignalMessage.model_validate_json(data)
    
    if manager.get(msg.to_id):
        await manager.send_to_user(msg.to_id,msg.model_dump_json())
    
    else:
        print(f"[SIGNAL] {msg.to_id} offline")