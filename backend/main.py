from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User, Log
from schemas import UserCreate, UserLogin, LogCreate, LogResponse, Token
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from datetime import datetime, timedelta
import uvicorn
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DriveBy.AI", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                to_remove.append(connection)
        
        for conn in to_remove:
            self.disconnect(conn)

manager = ConnectionManager() # Global instance

# Routes

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email, "role": new_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logs/upload", response_model=LogResponse)
async def upload_log(log: LogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can upload logs")
    
    new_log = Log(
        driver_id=current_user.id,
        fatigue_score=log.fatigue_score,
        emotion=log.emotion,
        drowsy_status=log.drowsy_status
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    # Broadcast to websocket
    await manager.broadcast(json.dumps({
        "fatigue_score": log.fatigue_score,
        "emotion": log.emotion,
        "drowsy_status": log.drowsy_status,
        "timestamp": datetime.now().isoformat()
    }))
    
    return new_log

@app.get("/logs/history", response_model=list[LogResponse])
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Drivers see their own logs, Family sees all (or specific driver if implemented)
    if current_user.role == "driver":
        return db.query(Log).filter(Log.driver_id == current_user.id).all()
    else:
        return db.query(Log).all()

@app.websocket("/ws/live-status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast received data (from driver) to all connected clients (family)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
