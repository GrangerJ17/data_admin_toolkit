# database.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Ensure .env variables are loaded

      

class PropertyDatabase:
    def __init__(self):
        self.connection = psycopg2.connect(
            database=os.getenv("PGNAME"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host="localhost",
            port=os.getenv("SYSPGPORT")
        )
        self.connection.autocommit = True

    def _init_schema_with_file_path(self):
        """Create tables if they don't exist"""
        conn = self.connection
        cur = conn.cursor()
        
        cur.execute("""
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
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scrape_history (
                id SERIAL PRIMARY KEY,
                property_id TEXT NOT NULL,
                scraped_at TIMESTAMP NOT NULL,
                job_url TEXT NOT NULL,
                vectorised BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (property_id) REFERENCES properties (property_id)
            )
        """)
        
        # Index for faster lookups
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_property_id 
            ON scrape_history(property_id)
        """)

    def upsert_property(self, property_data, scrape_metadata):
        """Insert new property or update existing one"""
        conn = self.connection
        cur = conn.cursor()

        # Check if property exists
        cur.execute(
            "SELECT property_id FROM properties WHERE property_id = %s",
            (property_data["id"],)
        )
        exists = cur.fetchone() is not None

        if exists:
            print("already exists", property_data)

            # Fetch current listing using property_id
            cur.execute(
                "SELECT * FROM properties WHERE property_id = %s",
                (property_data["id"],)
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("Record marked as exists but not found")

            # Convert row to dict
            column_names = [desc[0] for desc in cur.description]
            current_listing = dict(zip(column_names, row))

            # Update overlapping fields except DB PK
            update_fields = {
                key: value
                for key, value in property_data.items()
                if key in current_listing and key != "id"
            }

            if update_fields:
                set_clause = ", ".join(f"{key} = %s" for key in update_fields)
                values = list(update_fields.values()) + [property_data["id"]]

                sql = f"""
                    UPDATE properties
                    SET {set_clause}
                    WHERE property_id = %s
                """
                cur.execute(sql, values)

        else:
            # Insert new property
            cur.execute("""
                INSERT INTO properties (
                    property_id, price, bedrooms,
                    bathrooms, carspaces, description, 
                    property_type, state, postcode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            ) VALUES (%s, %s, %s)
        """, (
            property_data["id"],
            scrape_metadata["scraped_at"],
            scrape_metadata["job_url"]
        ))

        return "updated" if exists else "created"

    def get_property(self, property_id):
        """Get a single property by ID"""
        conn = self.connection
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM properties WHERE property_id = %s",
            (property_id,)
        )
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            return dict(zip(column_names, row))
        return None

    def get_all_properties(self):
        """Get all properties"""
        conn = self.connection
        cur = conn.cursor()
        cur.execute("SELECT * FROM properties ORDER BY updated_at DESC")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_scrape_history(self, property_id):
        """Get scrape history for a property"""
        conn = self.connection
        cur = conn.cursor()
        cur.execute("""
            SELECT scraped_at, job_url 
            FROM scrape_history 
            WHERE property_id = %s
            ORDER BY scraped_at DESC
        """, (property_id,))
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return [dict(zip(column_names, row)) for row in rows]

    def get_stats(self):
        """Get database statistics"""
        conn = self.connection
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM properties")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scrape_history")
        scrapes = cur.fetchone()[0]
        cur.execute("SELECT AVG(price) FROM properties")
        avg_price = cur.fetchone()[0]
        return {
            "total_properties": total,
            "total_scrapes": scrapes,
            "average_price": avg_price
        }

    def add_column(self, new_col: str, table_name: str):
        conn = self.connection
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_col}")

    def delete_dupes(self):
        conn = self.connection
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM scrape_history
            WHERE id NOT IN (
                SELECT MIN(id) AS id
                FROM scrape_history
                GROUP BY property_id
            )
        """)

    def test(self):
        conn = self.connection
        cur = conn.cursor()
        cur.execute("SELECT * FROM scrape_history")
        print(cur.fetchall())


if __name__ == "__main__":
    db = PropertyDatabase()
    db._init_schema_with_file_path()
    print(db.test())

