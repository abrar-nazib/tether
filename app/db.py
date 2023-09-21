ENV = "prod" # dev or prod

import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional

DB_NAME = "tether" 
DB_USER = "postgres" if ENV=="dev" else "tether"
DB_HOST = "localhost" if ENV=="dev" else "dpg-ck4ki4s2kpls73ejdq80-a.singapore-postgres.render.com"
DB_PASSWORD = "root" if ENV=="dev" else "j8GRreGlg2rTgodBQQt1idGklzJrZaRi"
DB_PORT = "5432"

conn = None
cursor = None

# pydantic model for signal data
class SignalData(BaseModel):
    lat: float
    lng: float
    tower_distance: float
    altitude: float
    image: Optional[bytes] = None
    detection_data: Optional[str] = None
    signal_strength: float
    

class DroneCommand(BaseModel):
    lat: float
    lng: float

    
# Database Connection
def connect_db():
    while True:
        print("Connecting to Database")
        try:
            global conn
            global cursor
            conn = psycopg2.connect(
                user=DB_USER,
                host=DB_HOST,
                database=DB_NAME,
                password=DB_PASSWORD,
                port=DB_PORT,
                cursor_factory=RealDictCursor,
            )
            
            cursor = conn.cursor()
            print("Database Connected")
            break
        except Exception as e:
            print("Database Connection Error: ", e)
          
# Create Table
def create_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS signal_data (
        id serial PRIMARY KEY,
        timestamp timestamp DEFAULT CURRENT_TIMESTAMP,
        lat double precision,
        lng double precision,
        tower_distance double precision,
        altitude double precision,
        image bytea,  
        detection_data text,
        signal_strength double precision
    );""")
    conn.commit()

# Insert Data
def insert_data(lat, lng, tower_distance, altitude, signal_strength, image=None, detection_data=None):
    try:
        
        # Insert query
        insert_query = """
        INSERT INTO signal_data (lat, lng, tower_distance, altitude, image, detection_data, signal_strength)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        # Data to insert
        data = (lat, lng, tower_distance, altitude, image, detection_data, signal_strength)
        
        # Execute the insert query
        cursor.execute(insert_query, data)
        
        # Commit the transaction
        conn.commit()
        
        # print("Data inserted successfully.")
    except Exception as e:
        print(f"Error: {e}")


# Get data (Limit 1000)
def get_data():
    try:
        cursor.execute("SELECT * FROM signal_data ORDER BY timestamp DESC LIMIT 1000;")
        data = cursor.fetchall()
        # convert data to dictionary format
        data = [dict(row) for row in data]
        return data
    except Exception as e:
        print(f"Error: {e}")