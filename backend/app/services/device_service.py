from datetime import datetime, timedelta

from app.database.connection import get_connection
from app.models.device import Device


def row_to_device(row) -> Device:
    return Device(
        device_id=row["device_id"],
        firmware_version=row["firmware_version"],
        ip_address=row["ip_address"],
        status=row["status"],
        last_seen=datetime.fromisoformat(row["last_seen"]),
    )


def register_device(
    device_id: str,
    firmware_version: str,
    ip_address: str,
) -> Device:

    connection = get_connection()

    existing_device = connection.execute(
        "SELECT device_id FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    if existing_device is not None:
        connection.close()
        raise ValueError("Device already registered")

    existing_ip = connection.execute(
        "SELECT device_id FROM devices WHERE ip_address = ?", (ip_address,)
    ).fetchone()
    if existing_ip is not None:
        connection.close()
        raise ValueError(f"IP address already assigned to {existing_ip['device_id']}")

    now = datetime.now()

    connection.execute(
        """
        INSERT INTO devices (
            device_id,
            firmware_version,
            ip_address,
            status,
            last_seen,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            device_id,
            firmware_version,
            ip_address,
            "online",
            now.isoformat(),
            now.isoformat(),
        ),
    )

    connection.commit()

    row = connection.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    connection.close()

    return row_to_device(row)


def get_all_devices() -> list[Device]:
    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM devices ORDER BY created_at"
    ).fetchall()

    connection.close()

    return [row_to_device(row) for row in rows]


def get_device(device_id: str) -> Device | None:
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return row_to_device(row)


def heartbeat_device(device_id: str) -> Device | None:
    connection = get_connection()

    existing_device = connection.execute(
        "SELECT device_id FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    if existing_device is None:
        connection.close()
        return None

    now = datetime.now()

    connection.execute(
        """
        UPDATE devices
        SET status = CASE
            WHEN status = 'isolated' THEN 'isolated'
            ELSE 'online'
        END,
        last_seen = ?
        WHERE device_id = ?
        """,
        (now.isoformat(), device_id),
    )

    connection.commit()

    row = connection.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    connection.close()

    return row_to_device(row)


def update_device_statuses() -> None:
    connection = get_connection()

    now = datetime.now()
    cutoff = now - timedelta(seconds=15)

    connection.execute(
        """
        UPDATE devices
        SET status = 'offline'
        WHERE last_seen < ?
            AND status != 'isolated'
        """,
        (cutoff.isoformat(),),
    )

    connection.commit()
    connection.close()


def get_device_by_ip(ip_address: str) -> Device | None:
    """Find a registered device using its IP address."""
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM devices WHERE ip_address = ?",
        (ip_address,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return row_to_device(row)

def isolate_device(device_id: str) -> Device | None:
    """Mark a device as isolated after suspicious activity detection."""

    connection = get_connection()

    existing_device = connection.execute(
        "SELECT device_id FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    if existing_device is None:
        connection.close()
        return None

    connection.execute(
        """
        UPDATE devices
        SET status = ?
        WHERE device_id = ?
        """,
        ("isolated", device_id),
    )

    connection.commit()

    row = connection.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    connection.close()

    return row_to_device(row)
