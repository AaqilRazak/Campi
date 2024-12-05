from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
from datetime import datetime, timedelta
import logging
import aiosqlite
from typing import Optional
from CampusQueryMapper import CampusDemoQueryMapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class PromptRequest(BaseModel):
    prompt: str

class SessionCreate(BaseModel):
    device_type: Optional[str] = None
    browser_agent: Optional[str] = None

class MessageCreate(BaseModel):
    message: str
    sender: str
    timestamp: str

# Database initialization
async def init_db():
    async with aiosqlite.connect('chat_history.db') as db:
        # Create existing tables
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

        # Create Campus Information tables
        await db.execute('''
            CREATE TABLE IF NOT EXISTS CampusInformation (
                BuildingID INTEGER PRIMARY KEY AUTOINCREMENT,
                BuildingName TEXT NOT NULL,
                BuildingAddress TEXT NOT NULL,
                BuildingHours TEXT,
                ContactInfo TEXT,
                Description TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS EventInformation (
                EventID INTEGER PRIMARY KEY AUTOINCREMENT,
                EventName TEXT NOT NULL,
                EventDateTime DATETIME NOT NULL,
                EventLocationID INTEGER NOT NULL,
                EventDescription TEXT,
                OrganizerContact TEXT,
                FOREIGN KEY (EventLocationID) REFERENCES CampusInformation(BuildingID)
            )
        ''')
        
        # Insert sample data for testing if needed
        await db.execute('''
            INSERT OR IGNORE INTO CampusInformation 
            (BuildingName, BuildingAddress, BuildingHours, ContactInfo, Description)
            VALUES 
            ('Library', '123 Campus Drive', '7:00 AM - 2:00 AM', '555-0123', 'Main campus library with quiet study spaces'),
            ('Student Center', '456 Campus Drive', '6:00 AM - 12:00 AM', '555-0124', 'Student hub with dining options and study areas'),
            ('Coffee Shop', '789 Campus Drive', '7:00 AM - 10:00 PM', '555-0125', 'Campus coffee shop with study tables')
        ''')
        
        await db.commit()

async def get_db():
    db = await aiosqlite.connect('chat_history.db')
    try:
        yield db
    finally:
        await db.close()

# Default test user ID for development
TEST_USER_ID = 1

@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Database initialized successfully")

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
        logger.error(f"Error fetching sessions: {str(e)}")
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
        logger.error(f"Error creating session: {str(e)}")
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
        logger.error(f"Error fetching messages: {str(e)}")
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
        logger.error(f"Error saving message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save message")
    
@app.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: aiosqlite.Connection = Depends(get_db)):
    try:
        # First delete associated messages
        await db.execute('''
            DELETE FROM MessageHistory 
            WHERE SessionID = ?
        ''', (session_id,))
        
        # Then delete the session
        await db.execute('''
            DELETE FROM SessionLogs 
            WHERE SessionID = ?
        ''', (session_id,))
        
        await db.commit()
        return {"status": "success", "message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")    

@app.post("/generate")
async def generate_text(prompt_request: PromptRequest, db: aiosqlite.Connection = Depends(get_db)):
    try:
        prompt = prompt_request.prompt.strip()
        logger.info(f"Received prompt: {prompt}")
        
        # Use the query mapper to handle the templated question
        query_mapper = CampusDemoQueryMapper(db)
        db_response = await query_mapper.match_and_execute(prompt)
        
        if not db_response:
            return {
                "response": "I'm not sure how to answer that question. Please select one of the provided options."
            }
        
        # Only proceed with LLM if we have database response
        try:
            llm_prompt = f"Act as a helpful campus assistant. Using only this accurate information: {db_response}, generate a natural, conversational response to: {prompt}"
            logger.info(f"Sending prompt to LLM: {llm_prompt}")
            
            # Check if ollama is available
            check_ollama = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            logger.info(f"Available models: {check_ollama.stdout}")
            
            process = subprocess.run(
                ["ollama", "run", "llama3.2:3b"], # Changed model name
                input=llm_prompt,
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # Increased timeout
            )
            
            llm_response = process.stdout.strip()
            logger.info(f"LLM response received: {llm_response}")
            
            if llm_response and len(llm_response) > 20:  # Basic validation
                logger.info("Using LLM response")
                return {"response": llm_response}
            else:
                logger.info(f"LLM response failed validation, length: {len(llm_response) if llm_response else 0}")
            
        except subprocess.TimeoutExpired as te:
            logger.error(f"LLM timeout error: {str(te)}")
        except subprocess.CalledProcessError as ce:
            logger.error(f"LLM process error: {str(ce)}, stderr: {ce.stderr}")
        except Exception as llm_error:
            logger.error(f"LLM error: {str(llm_error)}")
        
        logger.info("Falling back to DB response")
        return {"response": db_response}
            
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)