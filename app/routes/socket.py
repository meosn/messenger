from fastapi import WebSocket,APIRouter,WebSocketDisconnect
from ..chat import handle_chat
from ..signaling import handle_signal
from ..connections import manager
from ..models import SignalMessage

router = APIRouter() #подключение wbsocket к fastApi
@router.websocket("/socket/{user_id}")
async def websocket_endpoint(socket:WebSocket, user_id:str):
    await manager.connect(user_id,socket)
    
    try: 
        while True:
            data = await socket.receive_text()
            msg = SignalMessage.model_validate_json(data)
            if msg.type == "chat":
                await handle_chat(msg)
            else:
                await handle_signal(data,socket)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)