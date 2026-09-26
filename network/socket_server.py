import socket
import json
import sys
from typing import Dict, Any, List

# Impor langsung dari modul core yang sudah dibuat Iqbal
from core.services import SERVICE_REGISTRY

# Cek apakah modul fault_injector milik Sandy sudah ada atau belum
try:
    from core.fault_injector import FaultInjector
except (ImportError, AttributeError):
    FaultInjector = None


class SocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 65432, fault_rate: float = 0.30):
        self.host = host
        self.port = port
        self.fault_rate = fault_rate
        
        # State status layanan: True = Aktif, False = Dinonaktifkan
        self.services_state: Dict[str, bool] = {
            svc: True for svc in SERVICE_REGISTRY.keys()
        }
        self.is_running = False

    def get_active_services(self) -> List[str]:
        return [svc for svc, is_active in self.services_state.items() if is_active]

    def all_services_disabled(self) -> bool:
        return not any(self.services_state.values())

    def start(self):
        """Menginisialisasi socket TCP dan mendengarkan koneksi masuk."""
        self.is_running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(5)
            server_sock.settimeout(1.0)
            
            print(f"[SERVER STARTED] Berjalan pada {self.host}:{self.port}")
            print(f"[INITIAL STATE] Layanan aktif: {self.get_active_services()}\n")

            try:
                while self.is_running and not self.all_services_disabled():
                    try:
                        client_sock, client_addr = server_sock.accept()
                        client_sock.settimeout(None)
                        print(f"[CONNECTED] Klien terhubung dari {client_addr}")
                        self._handle_client(client_sock)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"[ERROR] Terjadi masalah pada loop socket: {e}")
            except KeyboardInterrupt:
                print("\n[STOPPED] Server dihentikan secara manual.")
                return

            if self.all_services_disabled():
                print("\n[GRACEFUL SHUTDOWN] Seluruh 5 layanan telah dinonaktifkan.")
                print("[SHUTDOWN] Menghentikan proses server secara normal.")
                sys.exit(0)

    def _handle_client(self, client_sock: socket.socket):
        """Membaca aliran pesan berbasis JSON line-delimited (\\n)."""
        with client_sock:
            reader = client_sock.makefile("r", encoding="utf-8")
            
            while not self.all_services_disabled():
                line = reader.readline()
                if not line:
                    print("[DISCONNECTED] Klien menutup koneksi.")
                    break

                stripped_line = line.strip()
                if not stripped_line:
                    continue

                try:
                    message = json.loads(stripped_line)
                    self._dispatch_message(client_sock, message)
                except json.JSONDecodeError:
                    print(f"[INVALID JSON] Pesan tidak valid: {stripped_line}")
                    self.send_json(client_sock, {
                        "type": "ERROR",
                        "status": "MALFORMED_JSON",
                        "message": "Format pesan harus berupa JSON yang valid."
                    })

                if self.all_services_disabled():
                    break

    def _dispatch_message(self, client_sock: socket.socket, message: Dict[str, Any]):
        """Memvalidasi dan mengarahkan tipe pesan ke handler yang tepat."""
        msg_type = message.get("type")

        if msg_type == "REQUEST":
            self._handle_request(client_sock, message)
        elif msg_type == "ACK":
            self._handle_ack(client_sock, message)
        else:
            self.send_json(client_sock, {
                "type": "ERROR",
                "status": "UNKNOWN_TYPE",
                "message": f"Tipe pesan '{msg_type}' tidak dikenali oleh protokol."
            })

    def _execute_service(self, service: str, payload: Dict[str, Any]) -> Any:
        """Memanggil fungsi pemrosesan dari SERVICE_REGISTRY milik Iqbal."""
        func = SERVICE_REGISTRY[service]
        
        if service == "MATRIX_3X3":
            matrix_data = payload.get("matrix")
            if matrix_data is None:
                raise ValueError("Payload membutuhkan field 'matrix'")
            return func(matrix_data)
        else:
            text_data = payload.get("text", "")
            return func(text_data)

    def _handle_request(self, client_sock: socket.socket, message: Dict[str, Any]):
        req_id = message.get("request_id")
        service = message.get("service")
        payload = message.get("payload", {})

        # 1. Validasi apakah layanan terdaftar
        if service not in self.services_state:
            self.send_json(client_sock, {
                "type": "RESPONSE",
                "request_id": req_id,
                "service": service,
                "status": "NOT_FOUND",
                "message": f"Layanan '{service}' tidak tersedia di server."
            })
            return

        # 2. Cek apakah layanan masih aktif
        if not self.services_state[service]:
            print(f"[REJECTED] Permintaan '{service}' ditolak (layanan nonaktif).")
            self.send_json(client_sock, {
                "type": "RESPONSE",
                "request_id": req_id,
                "service": service,
                "status": "DISABLED",
                "message": f"Layanan {service} telah dinonaktifkan oleh server."
            })
            return

        # 3. Eksekusi fungsi
        try:
            actual_result = self._execute_service(service, payload)

            # 4. Terapkan Fault Injector jika class sudah diimplementasi oleh Sandy
            if FaultInjector and hasattr(FaultInjector, "apply"):
                final_result = FaultInjector.apply(service, actual_result, rate=self.fault_rate)
            else:
                final_result = actual_result

            response = {
                "type": "RESPONSE",
                "request_id": req_id,
                "service": service,
                "status": "SUCCESS",
                "result": final_result
            }
            print(f"[PROCESSED] Layanan '{service}' sukses dieksekusi. Mengirim respon.")
            self.send_json(client_sock, response)

        except Exception as e:
            print(f"[EXECUTION ERROR] Kesalahan komputasi pada '{service}': {e}")
            self.send_json(client_sock, {
                "type": "RESPONSE",
                "request_id": req_id,
                "service": service,
                "status": "ERROR",
                "message": str(e)
            })

    def _handle_ack(self, client_sock: socket.socket, message: Dict[str, Any]):
        req_id = message.get("request_id")
        service = message.get("service")
        status = message.get("status")

        action = "MAINTAINED"

        if status == "INCORRECT":
            if self.services_state.get(service, False):
                self.services_state[service] = False
                action = "DISABLED"
                print(f"[ACTION] Layanan '{service}' DINONAKTIFKAN karena klien mengirim ACK: INCORRECT.")
        elif status == "CORRECT":
            print(f"[ACTION] Layanan '{service}' diverifikasi BENAR oleh klien.")

        active_list = self.get_active_services()
        server_status = "RUNNING" if active_list else "TERMINATING"

        ack_confirm = {
            "type": "ACK_CONFIRM",
            "request_id": req_id,
            "service": service,
            "action": action,
            "active_services": active_list,
            "server_status": server_status
        }
        self.send_json(client_sock, ack_confirm)
        print(f"[ACK PROCESSED] Status server: {server_status} | Layanan tersisa: {len(active_list)}")

    def send_json(self, client_sock: socket.socket, payload: Dict[str, Any]):
        """Mengirim pesan terenkapsulasi JSON line-delimited (\\n)."""
        raw_data = (json.dumps(payload) + "\n").encode("utf-8")
        client_sock.sendall(raw_data)