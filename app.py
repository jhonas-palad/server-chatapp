from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect,
    Request, HTTPException
)
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from models import *

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

registered_users = [
    User(username="Jhonas", password="123", name="PALAD")
]
@app.get('/')
async def root():
    return {"msg": "hello"}


@app.post('/login')
async def login(user : Login):
    print(user)
    found_user = None
    for registered_user in registered_users:
        if registered_user.username == user.username:
            found_user = registered_user
            break
    
    if found_user:
        if found_user.password != user.password:
            raise HTTPException(401, detail="Wrong password")
    else:
        raise HTTPException(401, detail="No user found")

    return found_user.dict()
 
@app.post('/register')
async def register(user : User):
    print(user)

    for registered_user in registered_users:
        if registered_user.username == user.username:
            raise HTTPException(401, detail="User already exists")
    
    new_user = User(username = user.username, password = user.password, name = user.name)
    registered_users.append(new_user)
    return new_user
 
class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_text(data) 

manager = SocketManager()

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)