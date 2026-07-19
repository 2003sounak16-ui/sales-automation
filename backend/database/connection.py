import os
import sqlite3
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SQLiteTableBuilder:
    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name
        self._where_clause = []
        self._params = []
        self._action = None
        self._data = None
        self._columns = "*"

    def insert(self, data):
        self._action = "insert"
        self._data = data
        return self

    def update(self, data):
        self._action = "update"
        self._data = data
        return self

    def select(self, columns="*"):
        self._action = "select"
        self._columns = columns
        return self

    def eq(self, column, value):
        self._where_clause.append(f"{column} = ?")
        self._params.append(str(value))
        return self

    def execute(self):
        cursor = self.conn.cursor()
        
        if self._action == "insert":
            data = self._data.copy()
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat() + "Z"
            if self.table_name == "leads" and "updated_at" not in data:
                data["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Serialize JSON fields
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    data[k] = json.dumps(v)
            
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            sql = f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            self.conn.commit()
            
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (data["id"],))
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            result_data = [self._row_to_dict(row, columns)]
            return SQLiteResponse(result_data)

        elif self._action == "update":
            data = self._data.copy()
            if "updated_at" not in data:
                data["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Serialize JSON fields
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    data[k] = json.dumps(v)
            
            set_parts = [f"{k} = ?" for k in data.keys()]
            set_sql = ", ".join(set_parts)
            
            sql = f"UPDATE {self.table_name} SET {set_sql}"
            params = list(data.values())
            
            if self._where_clause:
                sql += " WHERE " + " AND ".join(self._where_clause)
                params.extend(self._params)
                
            cursor.execute(sql, params)
            self.conn.commit()
            
            # Retrieve updated rows
            sql_select = f"SELECT * FROM {self.table_name}"
            select_params = []
            if self._where_clause:
                sql_select += " WHERE " + " AND ".join(self._where_clause)
                select_params = self._params
            cursor.execute(sql_select, select_params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result_data = [self._row_to_dict(r, columns) for r in rows]
            return SQLiteResponse(result_data)

        elif self._action == "select":
            sql = f"SELECT {self._columns} FROM {self.table_name}"
            params = []
            if self._where_clause:
                sql += " WHERE " + " AND ".join(self._where_clause)
                params.extend(self._params)
                
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result_data = [self._row_to_dict(r, columns) for r in rows]
            return SQLiteResponse(result_data)

    def _row_to_dict(self, row, columns):
        if row is None:
            return None
        res = {}
        for col, val in zip(columns, row):
            if col in ("social_links", "details") and val:
                try:
                    res[col] = json.loads(val)
                except Exception:
                    res[col] = val
            else:
                res[col] = val
        return res

class SQLiteResponse:
    def __init__(self, data):
        self.data = data

class SQLiteFallbackClient:
    def __init__(self, db_path="local_db.sqlite"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            website TEXT,
            description TEXT,
            about_text TEXT,
            industry TEXT,
            country TEXT,
            contact_email TEXT,
            social_links TEXT DEFAULT '{}',
            ai_subject TEXT,
            ai_body TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_events (
            id TEXT PRIMARY KEY,
            lead_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def table(self, name):
        return SQLiteTableBuilder(self.conn, name)

# Select between Supabase or SQLite Fallback
db_client = None
is_supabase = False

if SUPABASE_URL and SUPABASE_KEY and "your-" not in SUPABASE_URL and "your-" not in SUPABASE_KEY:
    try:
        db_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        is_supabase = True
        print("Connected to Supabase successfully.")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}. Falling back to SQLite.")
        db_client = SQLiteFallbackClient()
else:
    print("Supabase credentials not configured in .env. Falling back to local SQLite.")
    db_client = SQLiteFallbackClient()

def get_db():
    return db_client
