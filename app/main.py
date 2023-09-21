from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.params import Body
from app import db
import time


app = FastAPI()

db.connect_db()
db.create_table()

d_commands = []
drone_position = {"lat": 0, "lng": 0}

@app.get("/")
async def root():
    return {"message": "Tethered Drone API Homepage"}

# API endpoint from where the ground station gets the signal data
@app.get("/signal-data")
async def get_signals():
    data = db.get_data()
    print(data)
    return data

# API endpoint where drone will send data
@app.post("/signal-data") 
async def post_signal(signal: db.SignalData = Body(...)):
    # print(signal)
    db.insert_data(signal.lat, signal.lng, signal.tower_distance, signal.altitude, signal.image, signal.detection_data)
    return {"message": "Signal data created successfully."}

# API endpoint from where the drone will get the ground station commands
@app.get("/drone-control/plan")
async def get_drone_commands():
    global d_commands
    # print(d_commands)
    d = []
    for elem in d_commands:
        d.append(elem.model_dump())
    return d

# API endpoint where the ground station will send the drone commands
@app.post("/drone-control/plan")
async def post_drone_commands(coords: list[db.DroneCommand] =Body(...)):
    global d_commands
    d_commands = coords
    return {"message": "Drone Commands Recieved"}


 
# API endpoint where the ground control station will get drone lattitude and longitude
@app.get("/drone-control/position")
async def get_drone_position():
    global drone_position
    data = drone_position
    return data
 
 # API endpoint where the drone will send its lattitude and longitude
@app.post("/drone-control/position")
async def post_drone_position(coords: db.DroneCommand = Body(...)):
    global drone_position
    drone_position = coords
    # print(f"[+] Drone Position: {drone_position}")
    return {"message": "Drone Position Recieved"}
 
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager=ConnectionManager() 

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    global d_commands
    await manager.connect(websocket)
    try:
        while True:
            if(d_commands != []):
                print("Recieved Drone Commands")
                await manager.send_personal_message(f"Drone Command", websocket)
                d_commands=[]
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left")
        print("Client left")

