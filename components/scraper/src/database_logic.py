# database.py
import sqlite3
from pathlib import Path
import os


# this file: parent/webscrape/database.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_DIR = PROJECT_ROOT / "database"
DB_PATH = DB_DIR / "properties.db"


class PropertyDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    property_id TEXT PRIMARY KEY,
                    price REAL,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    carspaces INTEGER,
                    postcode INTEGER,
                    property_type TEXT,
                    state TEXT,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scrape_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id TEXT NOT NULL,
                    scraped_at TIMESTAMP NOT NULL,
                    job_url TEXT NOT NULL,
                    vectorised BOOL DEFAULT 0,
                    FOREIGN KEY (property_id) REFERENCES properties (property_id)
                )
            """)
            
            # Index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_property_id 
                ON scrape_history(property_id)
            """)
            
            conn.commit()
    
    def upsert_property(self, property_data, scrape_metadata):
        """Insert new property or update existing one"""
 
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            # Check if property exists
            cur.execute(
                "SELECT property_id FROM properties WHERE property_id = ?",
                (property_data["id"],)
            )
            exists = cur.fetchone() is not None
            
            if exists:
                print("already exists", property_data)

                # Fetch current listing using property_id
                cur.execute(
                    "SELECT * FROM properties WHERE property_id = ?",
                    (property_data["id"],)
                )

                row = cur.fetchone()
                if row is None:
                    raise RuntimeError("Record marked as exists but not found")

                # Convert row safely
                column_names = [desc[0] for desc in cur.description]
                current_listing = dict(zip(column_names, row))

                # Update all overlapping fields except DB PK
                update_fields = {
                    key: value
                    for key, value in property_data.items()
                    if key in current_listing and key != "id"
                }

                if not update_fields:
                    print("No fields to update")
                    return

                set_clause = ", ".join(f"{key} = ?" for key in update_fields)
                values = list(update_fields.values()) + [property_data["id"]]

                sql = f"""
                    UPDATE properties
                    SET {set_clause}
                    WHERE property_id = ?
                """

                cur.execute(sql, values)

            else:
                # Insert new property
                cur.execute("""
                    INSERT INTO properties (
                        property_id, price, bedrooms,
                        bathrooms, carspaces, description, 
                        property_type, state, postcode
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    property_data["id"],
                    property_data["price"],
                    property_data["bedrooms"],
                    property_data["bathrooms"],
                    property_data["carspaces"],
                    property_data["description"],
                    property_data["property_type"],
                    property_data["state"],
                    property_data["postcode"] 
                ))
            
            # Always log the scrape
            cur.execute("""
                INSERT INTO scrape_history (
                    property_id, scraped_at, job_url
                ) VALUES (?, ?, ?)
            """, (
                property_data["id"],
                scrape_metadata["scraped_at"],
                scrape_metadata["job_url"]
            ))
            
            conn.commit()
            return "updated" if exists else "created"

            # Add to PropertyDatabase class

    def get_property(self, property_id):
        """Get a single property by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM properties WHERE property_id = ?",
                (property_id,)
            )
            return dict(cur.fetchone()) if cur.fetchone() else None

    def get_all_properties(self):
        """Get all properties"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM properties ORDER BY updated_at DESC")
            return [dict(row) for row in cur.fetchall()]

    def get_scrape_history(self, property_id):
        """Get scrape history for a property"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT scraped_at, job_url 
                FROM scrape_history 
                WHERE property_id = ?
                ORDER BY scraped_at DESC
            """, (property_id,))
            return [dict(row) for row in cur.fetchall()]

    def get_stats(self):
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            total = cur.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
            scrapes = cur.execute("SELECT COUNT(*) FROM scrape_history").fetchone()[0]
            avg_price = cur.execute("SELECT AVG(price) FROM properties").fetchone()[0]
            
            return {
                "total_properties": total,
                "total_scrapes": scrapes,
                "average_price": avg_price
            }
    
    def add_column(self, new_col: str, table_name: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""ALTER TABLE {table_name} ADD {new_col}""")

    def delete_dupes(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM scrape_history
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT MIN(id) AS id
                        FROM scrape_history
                        GROUP BY property_id
                    )
                )
                """)
            
            conn.commit()
            

    def test(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            meta = cursor.execute("SELECT * FROM scrape_history")

            print(meta.fetchall())
           
