from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import subprocess
import logging
import aiosqlite
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database functions
async def init_db():
    async with aiosqlite.connect('chat_history.db') as db:
        # Create tables
        await db.execute('''
            CREATE TABLE IF NOT EXISTS UserInformation (
                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                PasswordHash TEXT NOT NULL,
                Email TEXT NOT NULL UNIQUE,
                UserRoleID INTEGER NOT NULL,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS SessionLogs (
                SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                SessionStartTime DATETIME NOT NULL,
                SessionEndTime DATETIME,
                DeviceType TEXT,
                IPAddress TEXT,
                BrowserAgent TEXT,
                FOREIGN KEY (UserID) REFERENCES UserInformation(UserID)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS MessageHistory (
                MessageID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                SessionID INTEGER NOT NULL,
                Timestamp DATETIME NOT NULL,
                Sender TEXT CHECK(Sender IN ('User', 'Bot')) NOT NULL,
                MessageText TEXT NOT NULL,
                FOREIGN KEY (UserID) REFERENCES UserInformation(UserID),
                FOREIGN KEY (SessionID) REFERENCES SessionLogs(SessionID)
            )
        ''')
        
        # Insert a default user for testing
        await db.execute('''
            INSERT OR IGNORE INTO UserInformation 
            (Username, PasswordHash, Email, UserRoleID, FirstName, LastName)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('testuser', 'password', 'test@test.com', 1, 'Test', 'User'))
        
        await db.commit()

async def get_db():
    db = await aiosqlite.connect('chat_history.db')
    try:
        yield db
    finally:
        await db.close()

# Models
class PromptRequest(BaseModel):
    prompt: str

class SessionCreate(BaseModel):
    device_type: Optional[str] = None
    browser_agent: Optional[str] = None

class MessageCreate(BaseModel):
    message: str
    sender: str
    timestamp: str

TEST_USER_ID = 1  # Using a default test user

@app.on_event("startup")
async def startup_event():
    await init_db()
    logging.info("Database initialized successfully")

@app.get("/sessions")
async def get_sessions(db: aiosqlite.Connection = Depends(get_db)):
    try:
        async with db.execute('''
            SELECT s.*, m.MessageText 
            FROM SessionLogs s 
            LEFT JOIN MessageHistory m ON s.SessionID = m.SessionID 
            WHERE s.UserID = ? 
            GROUP BY s.SessionID
            ORDER BY s.SessionStartTime DESC
        ''', (TEST_USER_ID,)) as cursor:
            sessions = await cursor.fetchall()
            return {
                "sessions": [
                    {
                        "SessionID": row[0],
                        "SessionStartTime": row[2],
                        "FirstMessage": row[-1] or "New Chat"
                    } for row in sessions
                ]
            }
    except Exception as e:
        logging.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")

@app.post("/sessions")
async def create_session(session: SessionCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        current_time = datetime.now().isoformat()
        async with db.execute('''
            INSERT INTO SessionLogs 
            (UserID, SessionStartTime, DeviceType, BrowserAgent)
            VALUES (?, ?, ?, ?)
            RETURNING SessionID
        ''', (TEST_USER_ID, current_time, session.device_type, session.browser_agent)) as cursor:
            session_id = await cursor.fetchone()
            await db.commit()
            return {"sessionId": session_id[0]}
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: int, db: aiosqlite.Connection = Depends(get_db)):
    try:
        async with db.execute('''
            SELECT MessageID, Timestamp, Sender, MessageText
            FROM MessageHistory 
            WHERE SessionID = ?
            ORDER BY Timestamp
        ''', (session_id,)) as cursor:
            messages = await cursor.fetchall()
            return {
                "messages": [
                    {
                        "MessageID": row[0],
                        "Timestamp": row[1],
                        "Sender": row[2],
                        "MessageText": row[3]
                    } for row in messages
                ]
            }
    except Exception as e:
        logging.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

@app.post("/sessions/{session_id}/messages")
async def save_message(session_id: int, message: MessageCreate, db: aiosqlite.Connection = Depends(get_db)):
    try:
        await db.execute('''
            INSERT INTO MessageHistory 
            (UserID, SessionID, Timestamp, Sender, MessageText)
            VALUES (?, ?, ?, ?, ?)
        ''', (TEST_USER_ID, session_id, message.timestamp, message.sender, message.message))
        await db.commit()
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error saving message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save message")

@app.post("/generate")
async def generate_text(prompt_request: PromptRequest):
    prompt = prompt_request.prompt
    try:
        logging.info(f"Received prompt: {prompt}")
        
        process = subprocess.run(
            ["ollama", "run", "llama3.2:3b", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        
        response = process.stdout
        logging.info(f"Ollama Response: {response}")
        
        return {"response": response.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.stderr}")
        raise HTTPException(status_code=500, detail="Model generation failed")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")