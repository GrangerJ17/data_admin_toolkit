# database.py
import sqlite3
from pathlib import Path

class PropertyDatabase:
    def __init__(self, db_path="/Users/jamesgranger/rental_semantic_search/webscrape/temp_database/properties.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    property_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    price REAL,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    carspaces INTEGER,
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
        new = 0
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            # Check if property exists
            cur.execute(
                "SELECT property_id FROM properties WHERE property_id = ?",
                (property_data["id"],)
            )
            exists = cur.fetchone() is not None
            
            if exists:
                # Update existing property
                print("already exist", cur.fetchone(), property_data)
                cur.execute("SELECT * FROM properties WHERE property_id = ?", (property_data["id"]))
                current_listing = dict(cur.fetchone())
                changes = {
                    key: value
                    for key, value in property_data.items()
                    if current_listing.get(key) != value
                }

                if len(changes) > 0:
                    exists = None

                set_clause = ", ".join(f"{k} = ?" for k in changes)
                values = list(changes.values()) + [property_data["id"]]

                cur.execute(
                    f"UPDATE properties SET {set_clause} WHERE id = ?",
                    values
                )
            else:
                # Insert new property
                cur.execute("""
                    INSERT INTO properties (
                        property_id, title, price, bedrooms,
                        bathrooms, carspaces, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    property_data["id"],
                    property_data["title"],
                    property_data["price"],
                    property_data["bedrooms"],
                    property_data["bathrooms"],
                    property_data["carspaces"],
                    property_data["description"]
                ))
                new = 1
                print("new_listing added")
            
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
            

    def new(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scrape_history")

            # The cursor description contains column information
            column_names = [description[0] for description in cursor.description]

            print(f"Table: users")
            print(f"Columns: {column_names}")

            # You can also get more details
            print("\nColumn Details (Name, Type, Display Size, Internal Size, Precision, Scale, Null OK):")
            for col in cursor.description:
                print(col)

db = PropertyDatabase()