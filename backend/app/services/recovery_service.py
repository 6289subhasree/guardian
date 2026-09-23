from app.database.connection import get_connection
from app.services.device_service import get_device, row_to_device


def recover_device(device_id: str):
    """Explicitly recover an isolated device and bring it back online."""

    device = get_device(device_id)

    if device is None:
        return None

    if device.status != "isolated":
        raise ValueError("Device is not isolated")

    connection = get_connection()

    connection.execute(
        """
        UPDATE devices
        SET status = ?
        WHERE device_id = ?
        """,
        ("online", device_id),
    )

    connection.commit()

    row = connection.execute(
        "SELECT * FROM devices WHERE device_id = ?",
        (device_id,),
    ).fetchone()

    connection.close()

    return row_to_device(row)
