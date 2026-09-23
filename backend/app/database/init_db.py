from app.database.connection import get_connection


def initialize_database() -> None:
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            firmware_version TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            status TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            risk_score REAL NOT NULL,
            classification TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
