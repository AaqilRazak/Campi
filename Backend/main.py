from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
from datetime import datetime, timedelta
import logging
import aiosqlite
from typing import Optional
from CampusQueryMapper import CampusDemoQueryMapper
from passlib.hash import bcrypt

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

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

# Database initialization
async def init_db():
    logging.info("Starting database initialization...")
    
    async with aiosqlite.connect('chat_history.db') as db:
        # Create user-related tables
        logging.info("Creating user tables...")
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
            CREATE TABLE IF NOT EXISTS StudentOrganizations (
                OrgID INTEGER PRIMARY KEY AUTOINCREMENT,
                OrgName TEXT NOT NULL UNIQUE,
                OrgDescription TEXT,
                MeetingSchedule TEXT,
                MeetingLocationID INTEGER,
                IsActive BOOLEAN DEFAULT 1,
                FOREIGN KEY (MeetingLocationID) REFERENCES CampusInformation(BuildingID)
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
        logging.info("Creating campus tables...")
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

        # First ensure Recreation Center exists
        logging.info("Setting up Recreation Center...")
        await db.execute('''
            INSERT OR IGNORE INTO CampusInformation 
            (BuildingID, BuildingName, BuildingAddress, BuildingHours, Description)
            VALUES 
            (3, 'Recreation Center', '601 University Drive', '6:00-23:00', 
             'Main campus recreation facility with multiple sports and fitness amenities')
        ''')

        # Get Recreation Center ID
        async with db.execute(
            'SELECT BuildingID FROM CampusInformation WHERE BuildingName = ?', 
            ('Recreation Center',)
        ) as cursor:
            rec_center = await cursor.fetchone()
            if not rec_center:
                logging.error("Failed to find Recreation Center after insertion")
                return
            rec_center_id = rec_center[0]
            logging.info(f"Recreation Center ID: {rec_center_id}")

        # Create other tables that depend on CampusInformation
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

        # Clear existing events for today
        current_date = datetime.now().strftime('%Y-%m-%d')
        await db.execute('''
            DELETE FROM EventInformation 
            WHERE date(EventDateTime) = date(?)
        ''', (current_date,))

        # Insert today's events
        await db.execute(f'''
            INSERT INTO EventInformation 
            (EventName, EventDateTime, EventLocationID, EventDescription, OrganizerContact)
            VALUES 
            ('Game Night', '{current_date} 19:00:00', ?, 'Join us for board games and snacks!', 'events@txstate.edu'),
            ('Live Music', '{current_date} 20:00:00', ?, 'Local student bands performing live', 'music@txstate.edu')
        ''', (rec_center_id, rec_center_id))

        # Insert weekend sporting events
        saturday = datetime.now() + timedelta(days=(5 - datetime.now().weekday()))
        sunday = saturday + timedelta(days=1)

        await db.execute(f'''
            INSERT INTO EventInformation 
            (EventName, EventDateTime, EventLocationID, EventDescription, OrganizerContact)
            VALUES 
            ('Basketball Game', '{saturday.strftime("%Y-%m-%d")} 19:00:00', ?, 
             'Home Conference Game - Bobcats vs. Rivals (Students Free with ID)', 'sports@txstate.edu'),
            ('Swimming Meet', '{sunday.strftime("%Y-%m-%d")} 14:00:00', ?, 
             'Conference Championships - Multiple Schools Competing (Free Admission)', 'sports@txstate.edu'),
            ('Volleyball Match', '{saturday.strftime("%Y-%m-%d")} 15:00:00', ?, 
             'Conference Match - Bobcats vs. State (Students Free with ID)', 'sports@txstate.edu')
        ''', (rec_center_id, rec_center_id, rec_center_id))

        await db.execute('''
            INSERT OR IGNORE INTO StudentOrganizations 
            (OrgName, OrgDescription, MeetingSchedule, MeetingLocationID, IsActive)
            VALUES 
            ('Computer Science Club', 'Programming workshops and tech talks', 'Thursdays at 5:00 PM', 1, 1),
            ('Student Government', 'Campus leadership and advocacy', 'Mondays at 4:00 PM', 1, 1),
            ('Chess Club', 'Weekly tournaments and casual play', 'Wednesdays at 6:00 PM', 2, 1)
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS SportingEvents (
                EventID INTEGER PRIMARY KEY AUTOINCREMENT,
                EventName TEXT NOT NULL,
                EventDateTime DATETIME NOT NULL,
                VenueID INTEGER NOT NULL,
                EventDescription TEXT,
                TeamInfo TEXT,
                TicketInfo TEXT,
                FOREIGN KEY (VenueID) REFERENCES CampusInformation(BuildingID)
            )
        ''')

        # Second event insertion
        current_date = datetime.now()
        saturday = current_date + timedelta(days=(5 - current_date.weekday()))
        sunday = saturday + timedelta(days=1)

        await db.execute(f'''
            INSERT OR IGNORE INTO SportingEvents 
            (EventName, EventDateTime, VenueID, EventDescription, TeamInfo, TicketInfo)
            VALUES 
            ('Basketball Game', '{saturday.strftime("%Y-%m-%d")} 19:00:00', 3, 
             'Home Conference Game', 'Bobcats vs. Rivals', 'Students Free with ID'),
            ('Swimming Meet', '{sunday.strftime("%Y-%m-%d")} 14:00:00', 3, 
             'Conference Championships', 'Multiple Schools Competing', 'Free Admission'),
            ('Volleyball Match', '{saturday.strftime("%Y-%m-%d")} 15:00:00', 3, 
             'Conference Match', 'Bobcats vs. State', 'Students Free with ID')
        ''')

        # Create and populate BuildingAmenities
        logging.info("Setting up Building Amenities...")
        await db.execute('''
            CREATE TABLE IF NOT EXISTS BuildingAmenities (
                AmenityID INTEGER PRIMARY KEY AUTOINCREMENT,
                BuildingID INTEGER NOT NULL,
                AmenityName TEXT NOT NULL,
                Description TEXT,
                Location TEXT,
                AvailabilityHours TEXT,
                FOREIGN KEY (BuildingID) REFERENCES CampusInformation(BuildingID)
            )
        ''')

        # Clear existing amenities for Recreation Center
        await db.execute('DELETE FROM BuildingAmenities WHERE BuildingID = ?', (rec_center_id,))

        # Insert amenities
        amenities = [
            ('Badminton Courts', 'Four professional courts available', '2nd Floor', 'Open during facility hours'),
            ('Basketball Courts', 'Six full-size courts with maple flooring', '1st Floor', 'Open during facility hours'),
            ('Boxing Area', 'Heavy bags, speed bags, and boxing ring', 'Lower Level', '6:00 AM - 10:00 PM'),
            ('Cardio Zone', 'Treadmills, ellipticals, bikes, and rowing machines', '2nd Floor', '24/7 access'),
            ('Changing Rooms', 'Lockers, showers, and changing facilities', 'All Floors', 'Open during facility hours'),
            ('Computer Lab', 'Workstations and printing services available', 'Main Entrance', '8:00 AM - 8:00 PM'),
            ('Cycle Studio', 'Indoor cycling room with 30 bikes', '3rd Floor', 'Class schedule varies'),
            ('Dance Studios', 'Three mirrored studios with sprung floors', '3rd Floor', 'Class schedule varies'),
            ('Equipment Checkout', 'Free equipment rental with student ID', 'Main Desk', '7:00 AM - 9:00 PM'),
            ('Game Room', 'Foosball, ping pong, and pool tables', 'Lower Level', '10:00 AM - 10:00 PM')
        ]

        # Use parameterized query for safer insertion
        for amenity in amenities:
            await db.execute('''
                INSERT INTO BuildingAmenities 
                (BuildingID, AmenityName, Description, Location, AvailabilityHours)
                VALUES (?, ?, ?, ?, ?)
            ''', (rec_center_id, *amenity))

        # Verify amenities were inserted
        async with db.execute(
            'SELECT COUNT(*) FROM BuildingAmenities WHERE BuildingID = ?', 
            (rec_center_id,)
        ) as cursor:
            count = await cursor.fetchone()
            logging.info(f"Inserted {count[0]} amenities for Recreation Center")

        await db.commit()
        logging.info("Database initialization complete")

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
    logging.info("Application starting up...")
    await init_db()
    await init_default_users()

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
            llm_prompt = f"As Campi, you humanize the database reponses for the input prompt only. Here is the prompt: {prompt}, and database response: {db_response}."
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

@app.post("/login")
async def login(login_request: LoginRequest, db: aiosqlite.Connection = Depends(get_db)):
    try:
        logging.info("=== Login Attempt ===")
        logging.info(f"Username: {login_request.username}")
        logging.info(f"Password length: {len(login_request.password)}")
        
        # First check if users exist in database
        async with db.execute('SELECT COUNT(*) FROM UserInformation') as cursor:
            count = await cursor.fetchone()
            logging.info(f"Total users in database: {count[0]}")
        
        # Try to find the user
        async with db.execute('''
            SELECT UserID, Username, PasswordHash, UserRoleID, FirstName, LastName 
            FROM UserInformation 
            WHERE Username = ?
        ''', (login_request.username,)) as cursor:
            user = await cursor.fetchone()
            
        if not user:
            logging.warning(f"User not found: {login_request.username}")
            # List all usernames in database for debugging
            async with db.execute('SELECT Username FROM UserInformation') as cursor:
                users = await cursor.fetchall()
                logging.info(f"Available users: {[u[0] for u in users]}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logging.info(f"Found user: {user[1]} with role {user[3]}")
        logging.info(f"Stored password hash: {user[2]}")
        
        try:
            # Verify password
            is_valid = bcrypt.verify(login_request.password, user[2])
            logging.info(f"Password verification result: {is_valid}")
            
            if not is_valid:
                logging.warning(f"Invalid password for user: {login_request.username}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        except Exception as e:
            logging.error(f"Password verification error: {str(e)}")
            logging.error(f"Password type: {type(login_request.password)}")
            logging.error(f"Hash type: {type(user[2])}")
            raise HTTPException(status_code=500, detail=f"Error verifying credentials: {str(e)}")
            
        role_map = {1: 'student', 2: 'admin', 3: 'guest'}
        
        response_data = {
            "id": user[0],
            "username": user[1],
            "role": role_map.get(user[3], 'guest'),
            "firstName": user[4],
            "lastName": user[5]
        }
        logging.info(f"Login successful for user: {login_request.username}")
        logging.info(f"Returning data: {response_data}")
        return response_data
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/change-password")
async def change_password(request: PasswordChangeRequest, db: aiosqlite.Connection = Depends(get_db)):
    try:
        # First verify the current password
        async with db.execute('''
            SELECT UserID, PasswordHash 
            FROM UserInformation 
            WHERE Username = ?
        ''', (request.username,)) as cursor:
            user = await cursor.fetchone()
            
        if not user or not bcrypt.verify(request.old_password, user[1]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update to new password
        hashed_new_password = bcrypt.hash(request.new_password)
        await db.execute('''
            UPDATE UserInformation 
            SET PasswordHash = ?
            WHERE UserID = ?
        ''', (hashed_new_password, user[0]))
        
        await db.commit()
        return {"message": "Password updated successfully"}
            
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to change password")

# Add this function after init_db()
async def init_default_users():
    logging.info("Initializing default users...")
    try:
        async with aiosqlite.connect('chat_history.db') as db:
            # Default test accounts
            default_users = [
                ('student', 'studentpass', 'student@example.com', 1, 'Student', 'User'),
                ('admin', 'adminpass', 'admin@example.com', 2, 'Admin', 'User'),
                ('guest', 'pass', 'guest@example.com', 3, 'Guest', 'User')
            ]
            
            # First check existing users
            async with db.execute('SELECT Username FROM UserInformation') as cursor:
                existing = await cursor.fetchall()
                logging.info(f"Existing users: {[user[0] for user in existing]}")
            
            for username, password, email, role_id, first_name, last_name in default_users:
                try:
                    # Check if user exists
                    async with db.execute('SELECT Username FROM UserInformation WHERE Username = ?', (username,)) as cursor:
                        existing_user = await cursor.fetchone()
                        
                        if not existing_user:
                            hashed_password = bcrypt.hash(password)
                            await db.execute('''
                                INSERT INTO UserInformation 
                                (Username, PasswordHash, Email, UserRoleID, FirstName, LastName)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (username, hashed_password, email, role_id, first_name, last_name))
                            logging.info(f"Created default user: {username}")
                        else:
                            logging.info(f"User already exists: {username}")
                except Exception as e:
                    logging.error(f"Error creating user {username}: {str(e)}")
            
            await db.commit()
            
            # Verify users after creation
            async with db.execute('SELECT Username, UserRoleID FROM UserInformation') as cursor:
                users = await cursor.fetchall()
                logging.info(f"All users after initialization: {users}")
                
    except Exception as e:
        logging.error(f"Error in init_default_users: {str(e)}")

@app.get("/debug/users")
async def get_users(db: aiosqlite.Connection = Depends(get_db)):
    try:
        async with db.execute('''
            SELECT UserID, Username, UserRoleID, FirstName, LastName 
            FROM UserInformation
        ''') as cursor:
            users = await cursor.fetchall()
            return {
                "users": [
                    {
                        "id": user[0],
                        "username": user[1],
                        "role": user[2],
                        "firstName": user[3],
                        "lastName": user[4]
                    } for user in users
                ]
            }
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)