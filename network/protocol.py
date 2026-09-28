import json
from typing import Dict, Any, Tuple, List

class ProtocolError(Exception):
    """Custom exception untuk kesalahan format dan validasi protokol JSON."""
    pass

def encode_message(data: Dict[str, Any]) -> bytes:
    """Mengubah dictionary Python menjadi bytes JSON line-delimited (diakhiri \\n)."""
    try:
        json_str = json.dumps(data) + "\n"
        return json_str.encode('utf-8')
    except Exception as e:
        raise ProtocolError(f"Gagal melakukan serialisasi JSON: {str(e)}")

def decode_message(raw_data: bytes) -> Dict[str, Any]:
    """Mengubah bytes yang diterima dari socket TCP menjadi dictionary Python."""
    try:
        text = raw_data.decode('utf-8').strip()
        if not text:
            raise ProtocolError("Pesan kosong diterima.")
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ProtocolError(f"Format JSON tidak valid: {str(e)}")
    except Exception as e:
        raise ProtocolError(f"Gagal melakukan deserialisasi data: {str(e)}")

def validate_message(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Memvalidasi struktur skema JSON untuk tipe REQUEST dan ACK."""
    if not isinstance(data, dict):
        return False, "Payload harus berupa objek JSON (dict)."

    msg_type = data.get("type")
    if not msg_type:
        return False, "Field 'type' wajib ada dalam pesan."

    if msg_type == "REQUEST":
        required_keys = {"type", "request_id", "service", "payload"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - set(data.keys())
            return False, f"REQUEST kekurangan field wajib: {missing}"
        if not isinstance(data.get("payload"), dict):
            return False, "Field 'payload' pada REQUEST harus berupa objek JSON."

    elif msg_type == "ACK":
        required_keys = {"type", "request_id", "service", "status"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - set(data.keys())
            return False, f"ACK kekurangan field wajib: {missing}"
        if data.get("status") not in {"CORRECT", "INCORRECT"}:
            return False, "Nilai field 'status' pada ACK harus 'CORRECT' atau 'INCORRECT'."

    else:
        return False, f"Tipe pesan '{msg_type}' tidak didukung oleh protokol."

    return True, "Valid"

def create_response(request_id: str, service: str, result: Any = None, is_disabled: bool = False) -> Dict[str, Any]:
    """Menyusun struktur dictionary response dari server."""
    if is_disabled:
        return {
            "type": "RESPONSE",
            "request_id": request_id,
            "service": service,
            "status": "DISABLED",
            "message": f"Layanan {service} telah dinonaktifkan oleh server."
        }
    return {
        "type": "RESPONSE",
        "request_id": request_id,
        "service": service,
        "status": "SUCCESS",
        "result": result
    }

def create_ack_confirm(request_id: str, service: str, action: str, active_services: List[str], is_terminating: bool = False) -> Dict[str, Any]:
    """Menyusun struktur dictionary konfirmasi ACK dari server."""
    return {
        "type": "ACK_CONFIRM",
        "request_id": request_id,
        "service": service,
        "action": action,
        "active_services": active_services,
        "server_status": "TERMINATING" if is_terminating else "RUNNING"
    }