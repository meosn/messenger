from pydantic import BaseModel
from typing import Any, Literal

class SignalMessage(BaseModel):
    type: Literal["offer", "answer", "ice", "chat"]
    from_id: str
    to_id: str
    payload: Any