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

    connection.execute("""CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL, source_ip TEXT NOT NULL,
        destination_ip TEXT NOT NULL, protocol TEXT NOT NULL,
        packet_length INTEGER NOT NULL, source_port INTEGER,
        destination_port INTEGER, tcp_flags TEXT, payload_length INTEGER NOT NULL,
        device_id TEXT
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS observations_time_idx ON observations(timestamp)")
    connection.execute("""CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL,
        temperature REAL NOT NULL, humidity REAL NOT NULL, timestamp TEXT NOT NULL
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS response_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL,
        action TEXT NOT NULL, outcome TEXT NOT NULL, detail TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
