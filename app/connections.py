from fastapi import WebSocket 
"""accept() — принять соединение
send_text() — отправить текст
receive_text() — получить текст"""

class ConnectionManager():
    def __init__(self):
        self.active_users: dict[str,WebSocket] = {} #id : socket
        
    async def connect(self,user_id:str,socket:WebSocket):
        await socket.accept()
        self.active_users[user_id] = socket
        print(f"[CONNECTION] {user_id}")
    
    def disconnect(self,user_id:str):
        if user_id in self.active_users:
            del self.active_users[user_id]
            print(f"[DISCONNECTED] {user_id}")
    
    def get(self,user_id:str) -> WebSocket | None:
        return self.active_users.get(user_id)
    
    async def send_to_user(self,user_id:str,message:str):
        socket = self.get(user_id)
        if socket:
            await socket.send_text(message)
            
manager = ConnectionManager()