import argparse
from network.socket_server import SocketServer

def main():
    parser = argparse.ArgumentParser(description="TCP Socket Server - Kelompok 7 Jaringan Komputer")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Alamat host binding (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=65432, help="Port server (default: 65432)")
    parser.add_argument("--fault-rate", type=float, default=0.30, help="Tingkat kemungkinan kesalahan acak (default: 0.30)")

    args = parser.parse_args()

    server = SocketServer(
        host=args.host,
        port=args.port,
        fault_rate=args.fault_rate
    )
    server.start()

if __name__ == "__main__":
    main()